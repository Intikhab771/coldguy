import os
import json
import mimetypes
from typing import Optional
from click import prompt
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from email.message import EmailMessage
import aiosmtplib
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from google.genai import types
import json
from playwright.async_api import async_playwright

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
queue = asyncio.Queue()
# A tripwire to wake up the scheduler instantly if settings change
frequency_event = asyncio.Event()

class JobApplicationData(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    resume_text: str
    user_name: str        
    user_links: str = ""

class ScrapeRequest(BaseModel):
    url: str

# --- THE SERVER'S MEMORY ---
GLOBAL_STATE = {
    "is_auto_mode": False,
    "frequency": 60,       
    "saved_campaign": [],  
    "emails_sent": 0,       
    "total_target": 1       
}

# 1. THE CHEF
async def email_worker():
    print("👷 Chef Online: Waiting for tasks...")
    while True:
        order = await queue.get()
        
        # Guard: Ensure we don't cook if target is already hit
        if GLOBAL_STATE["emails_sent"] >= GLOBAL_STATE["total_target"]:
            GLOBAL_STATE["is_auto_mode"] = False
            queue.task_done()
            continue
            
        target = order['target_email']
        print(f"🍳 Cooking Email to {target}...")
        
        try:
            msg = EmailMessage()
            msg.set_content(order['body'])
            msg["Subject"] = order['subject']
            msg["From"] = os.getenv("SENDER_EMAIL")
            msg["To"] = target
            
            if order.get('attachments'):
                for att in order['attachments']:
                    ctype, encoding = mimetypes.guess_type(att['filename'])
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    
                    msg.add_attachment(
                        att['bytes'], maintype=maintype, subtype=subtype, filename=att['filename']
                    )

            # Await the actual delivery handshake from the SMTP server
            await aiosmtplib.send(
                msg, hostname="smtp.gmail.com", port=465, use_tls=True,
                username=os.getenv("SENDER_EMAIL"), password=os.getenv("SENDER_PASSWORD")
            )
            print(f"✅ Delivered to {target} SMTP Server")
            
            # THE TOLERANCE: Slight delay to sync counter strictly with recipient inbox processing
            await asyncio.sleep(1.5)
            
            GLOBAL_STATE["emails_sent"] += 1 
            
            # Post-send guard: Stop clock if we just hit the target
            if GLOBAL_STATE["emails_sent"] >= GLOBAL_STATE["total_target"]:
                GLOBAL_STATE["is_auto_mode"] = False
                print("🎯 Target reached! Auto-campaign terminated.")
                
        except Exception as e:
            print(f"❌ Error sending to {target}: {e}")
        finally:
            queue.task_done()

# 2. THE CLOCK (Optimized Event-Driven Scheduler)
async def campaign_scheduler():
    print("⏰ Automation Clock Online (Event-Driven)...")
    
    while True:
        if GLOBAL_STATE["is_auto_mode"] and GLOBAL_STATE["saved_campaign"]:
            # Auto-kill if target was reached externally
            if GLOBAL_STATE["emails_sent"] >= GLOBAL_STATE["total_target"]:
                GLOBAL_STATE["is_auto_mode"] = False
                await asyncio.sleep(1)
                continue

            # 1. Fire the emails
            print("⏳ CLOCK TRIGGERED! Injecting emails into the queue.")
            for order in GLOBAL_STATE["saved_campaign"]:
                if GLOBAL_STATE["emails_sent"] + queue.qsize() < GLOBAL_STATE["total_target"]:
                    await queue.put(order)
            
            # 2. Go to deep sleep for the exact frequency duration
            try:
                # wait_for will pause completely for GLOBAL_STATE["frequency"] seconds.
                # IF frequency_event is triggered before time runs out, it wakes up instantly.
                await asyncio.wait_for(frequency_event.wait(), timeout=GLOBAL_STATE["frequency"])
                
                # If we reach this line, it means the user moved the slider and tripped the wire.
                # We clear the wire and loop back to adjust to the new reality.
                print("⚡ Scheduler interrupted by live setting change! Recalculating...")
                frequency_event.clear()
                
            except asyncio.TimeoutError:
                # If we get a TimeoutError, it means the wire was NOT tripped, 
                # and the full frequency time elapsed naturally. Time to loop and fire again!
                pass
                
        else:
            # If auto-mode is off, check again in a bit
            await asyncio.sleep(2)

# 3. STARTUP MANAGER
@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(email_worker())
    scheduler_task = asyncio.create_task(campaign_scheduler())
    yield 
    worker_task.cancel()
    scheduler_task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"]
)

# --- NEW: LIVE FREQUENCY UPDATE ENDPOINT ---
@app.post("/api/update-frequency")
async def update_frequency(frequency: int = Form(...)):
    GLOBAL_STATE["frequency"] = frequency
    print(f"🎚️ Live Frequency Update: {frequency}s")
    
    # Trip the wire! Wake the scheduler up instantly to apply the new time.
    frequency_event.set() 
    
    return {"status": "Success", "frequency": GLOBAL_STATE["frequency"]}

# --- STATUS ENDPOINT ---
@app.get("/api/campaign-status")
async def get_campaign_status():
    return {
        "emails_sent": GLOBAL_STATE["emails_sent"],
        "total_target": GLOBAL_STATE["total_target"],
        "is_auto_mode": GLOBAL_STATE["is_auto_mode"]
    }

# 4. THE WAITER
@app.post("/api/send-bulk")
async def handle_bulk_campaign(
    campaign_data: str = Form(...),
    is_auto_mode: str = Form("false"),  
    frequency: int = Form(60),
    total_target: int = Form(1),
    attachments: list[UploadFile] = File([]) 
):
    email_orders = json.loads(campaign_data)
    
    # Reset tracking
    GLOBAL_STATE["emails_sent"] = 0
    GLOBAL_STATE["total_target"] = total_target
    
    file_data_list = []
    for file in attachments:
        file_bytes = await file.read()
        file_data_list.append({
            "filename": file.filename,
            "bytes": file_bytes
        })
        
    for order in email_orders:
        order['attachments'] = file_data_list
        
    if is_auto_mode == "true":
        GLOBAL_STATE["is_auto_mode"] = True
        GLOBAL_STATE["frequency"] = frequency
        GLOBAL_STATE["saved_campaign"] = email_orders
        return {"status": "Success", "message": f"🤖 Auto-Mode Started! Firing every {frequency} seconds."}
    else:
        GLOBAL_STATE["is_auto_mode"] = False
        for order in email_orders:
            # Ensure even manual sends respect the cap
            if GLOBAL_STATE["emails_sent"] + queue.qsize() < GLOBAL_STATE["total_target"]:
                await queue.put(order)
        return {"status": "Success", "message": "📤 Sent manually once!"}

@app.post("/api/stop-auto")
async def stop_automation():
    print("🛑 Waiter received STOP command! Killing the clock.")
    GLOBAL_STATE["is_auto_mode"] = False
    GLOBAL_STATE["saved_campaign"] = []
    return {"status": "Success", "message": "🛑 Automation successfully stopped!"}

@app.post("/api/generate-email")
async def generate_cover_letter(data: JobApplicationData):
    print(f"🧠 AI Writer activating for {data.company_name}...")
    
    prompt = f"""
    You are an expert career coach writing a cold email.
    
    Job: {data.job_title} at {data.company_name}
    Description: {data.job_description}
    
    Applicant Background: {data.resume_text}
    Applicant Name: {data.user_name}
    Applicant Links: {data.user_links}
    
    Rules:
    1. Write a confident, 3-paragraph email.
    2. DO NOT use ANY placeholders like [Hiring Manager Name] or [Your Phone Number]. 
       If you don't know the manager's name, just start with "Hi Team," or "Hi Hiring Manager,".
       Sign off using exactly the Applicant Name and Applicant Links provided.
    3. You MUST respond in strict JSON format with exactly two keys: "subject" and "body".
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if not response.text:
            raise ValueError("AI did not return any content.")
            
        email_data = json.loads(response.text)
        print("✅ AI successfully generated and parsed the email!")
        
        return {
            "status": "Success", 
            "subject": email_data["subject"],
            "body": email_data["body"]
        }
        
    except Exception as e:
        print(f"❌ Error generating email: {e}")
        return {"status": "Error", "message": str(e)}

@app.post("/api/scrape")
async def scrape_job_description(request: ScrapeRequest):
    print(f"🕵️‍♂️ Scraper deploying to: {request.url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(request.url, wait_until="domcontentloaded", timeout=60000)
            raw_text = await page.evaluate("document.body.innerText")
            await browser.close()
            
        print("📄 Text secured. Handing over to AI for extraction...")
            
        prompt = f"""
        You are a highly accurate data extraction bot. 
        I am giving you the raw text scraped from a webpage.
        Find the job posting details hidden inside this text.
        
        Raw Text:
        {raw_text[:15000]} 
        
        Extract the following and return ONLY strict JSON:
        - "job_title": The exact title of the role.
        - "company_name": The company offering the job.
        - "job_description": A 2 to 3 sentence summary of the role's requirements.
        - "target_email": Hunt for ANY contact email address in the text (e.g., founders, recruiters, careers@). If none exists, return an empty string "".
        """
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if not response.text:
            raise ValueError("AI returned empty data.")
            
        raw_json_data = json.loads(response.text)
        
        # --- THE FIX: Handle cases where the AI wraps the JSON in an array ---
        if isinstance(raw_json_data, list):
            extracted_data = raw_json_data[0] if len(raw_json_data) > 0 else {}
        else:
            extracted_data = raw_json_data
            
        print(f"✅ Successfully scraped and parsed: {extracted_data.get('company_name', 'Unknown')}")
        
        return {"status": "Success", "data": extracted_data}
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return {"status": "Error", "message": str(e)}
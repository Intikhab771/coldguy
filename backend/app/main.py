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
    "frequency": 60,       # Default 60 seconds
    "saved_campaign": []   # Holds the emails & attachments for the loop
}

# 1. THE CHEF
async def email_worker():
    print("👷 Chef Online: Waiting for tasks...")
    while True:
        order = await queue.get()
        target = order['target_email']
        print(f"🍳 Cooking Email to {target}...")
        
        try:
            msg = EmailMessage()
            msg.set_content(order['body'])
            msg["Subject"] = order['subject']
            msg["From"] = os.getenv("SENDER_EMAIL")
            msg["To"] = target
            
            # Loop through multiple attachments if they exist
            if order.get('attachments'):
                for att in order['attachments']:
                    ctype, encoding = mimetypes.guess_type(att['filename'])
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    
                    msg.add_attachment(
                        att['bytes'], maintype=maintype, subtype=subtype, filename=att['filename']
                    )

            await aiosmtplib.send(
                msg, hostname="smtp.gmail.com", port=465, use_tls=True,
                username=os.getenv("SENDER_EMAIL"), password=os.getenv("SENDER_PASSWORD")
            )
            print(f"✅ Delivered to {target}")
        except Exception as e:
            print(f"❌ Error sending to {target}: {e}")
        finally:
            queue.task_done()

# 2. THE CLOCK (The Automator)
async def campaign_scheduler():
    print("⏰ Automation Clock Online...")
    while True:
        # If auto mode is ON, and we have saved emails
        if GLOBAL_STATE["is_auto_mode"] and GLOBAL_STATE["saved_campaign"]:
            print(f"⏳ CLOCK TRIGGERED! Injecting {len(GLOBAL_STATE['saved_campaign'])} emails into the queue.")
            
            # Dump a copy of the saved emails into the Chef's queue
            for order in GLOBAL_STATE["saved_campaign"]:
                await queue.put(order)
            
            # Go to sleep until the next frequency cycle
            await asyncio.sleep(GLOBAL_STATE["frequency"])
        else:
            # If auto is OFF, just wait 3 seconds and check again
            await asyncio.sleep(3)

# 3. STARTUP MANAGER
@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(email_worker())
    scheduler_task = asyncio.create_task(campaign_scheduler()) # Turn the clock on!
    yield 
    worker_task.cancel()
    scheduler_task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"]
)

# 4. THE WAITER (Upgraded for Settings and Multiple Files)
@app.post("/api/send-bulk")
async def handle_bulk_campaign(
    campaign_data: str = Form(...),
    is_auto_mode: str = Form("false"),  # Catch the toggle switch
    frequency: int = Form(60),          # Catch the timer
    attachments: list[UploadFile] = File([]) # Accept a list of files
):
    email_orders = json.loads(campaign_data)
    
    # Process all incoming files into memory
    file_data_list = []
    for file in attachments:
        file_bytes = await file.read()
        file_data_list.append({
            "filename": file.filename,
            "bytes": file_bytes
        })
        
    for order in email_orders:
        order['attachments'] = file_data_list
        
    # LOGIC: Check what the user wants to do
    if is_auto_mode == "true":
        # Save to memory and turn the clock ON
        GLOBAL_STATE["is_auto_mode"] = True
        GLOBAL_STATE["frequency"] = frequency
        GLOBAL_STATE["saved_campaign"] = email_orders
        return {"status": "Success", "message": f"🤖 Auto-Mode Started! Firing every {frequency} seconds."}
    else:
        # Turn the clock OFF and just send them immediately
        GLOBAL_STATE["is_auto_mode"] = False
        for order in email_orders:
            await queue.put(order)
        return {"status": "Success", "message": "📤 Sent manually once!"}

@app.post("/api/stop-auto")
async def stop_automation():
    print("🛑 Waiter received STOP command! Killing the clock.")
    
    # Wipe the server's memory
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
            
            await page.goto(request.url, wait_until="domcontentloaded", timeout=15000)
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
            
        extracted_data = json.loads(response.text)
        print(f"✅ Successfully scraped and parsed: {extracted_data.get('company_name', 'Unknown')}")
        
        return {"status": "Success", "data": extracted_data}
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return {"status": "Error", "message": str(e)}
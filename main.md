# FastAPI Email Campaign and Web Scraper

This document contains the source code for a FastAPI application that manages email campaigns, generates emails using AI, and scrapes job descriptions from websites.

---

## Imports
```python
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
import json  # Duplicate import, can be removed if desired.
from playwright.async_api import async_playwright
```

## Environment Setup and Client Initialization
def load environment variables and initialize Google GenAI client.
```python
dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
queue = asyncio.Queue()
```

## Data Models
definitions for request payloads.
```python
def class JobApplicationData(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    resume_text: str  
    user_name: str        
    user_links: str = ""

def class ScrapeRequest(BaseModel):
    url: str  
```

## Global State Management
defines server memory state.
```python
global_state = {
    "is_auto_mode": False,
    "frequency": 60,       # Default 60 seconds,
    "saved_campaign": []   # Holds the emails & attachments for the loop,
}
```
---
## Email Worker (Chef)
def email_worker():
description of email sending process with error handling.
```python
def async def email_worker():
    print("👷 Chef Online: Waiting for tasks...")
    while True:
        order = await queue.get()
        target = order['target_email']
        print(f"🍳 Cooking Email to {target}...")
        try:
            msg = EmailMessage()
            msg.set_content(order['body'])
            msg["Subject"] = order['subject']
'text'
the rest of the code continues as in the original script...
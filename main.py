from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import openai
import os
import base64
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jyotishai")

app = FastAPI()

# Allow CORS for mobile frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

class RashifalRequest(BaseModel):
    dob: str
    time: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = "English"

async def query_openai_text(prompt: str) -> str:
    logger.info(f"Sending OpenAI TEXT prompt: {prompt}")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert astrologer providing spiritual and astrological guidance."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"Received OpenAI TEXT response: {answer}")
        return answer
    except Exception as e:
        logger.error(f"OpenAI TEXT error: {e}")
        return f"Error from OpenAI: {str(e)}"

async def query_openai_vision(image_bytes: bytes, prompt: str) -> str:
    logger.info(f"Sending OpenAI VISION prompt: {prompt}")
    try:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=1000,
        )
        answer = response.choices[0].message.content.strip()
        logger.info(f"Received OpenAI VISION response: {answer}")
        return answer
    except Exception as e:
        logger.error(f"OpenAI VISION error: {e}")
        return f"Error from OpenAI: {str(e)}"

@app.post("/upload/palm")
async def upload_palm(file: UploadFile = File(...), language: Optional[str] = "English"):
    content = await file.read()
    logger.info(f"Received palm image: {file.filename}")
    prompt = f"Analyze this palm image for personality, fate, and health insights. Respond in {language}."
    result = await query_openai_vision(content, prompt)
    return {
        "status": "success",
        "summary": result
    }

@app.post("/upload/face")
async def upload_face(file: UploadFile = File(...), language: Optional[str] = "English"):
    content = await file.read()
    logger.info(f"Received face image: {file.filename}")
    prompt = f"Analyze this face image for emotional traits, personality, health markers, and expression cues. Respond in {language}."
    result = await query_openai_vision(content, prompt)
    return {
        "status": "success",
        "summary": result
    }

@app.post("/rashifal")
async def get_rashifal(data: RashifalRequest):
    logger.info(f"Rashifal request for DOB: {data.dob}, Time: {data.time}, Location: {data.location}, Language: {data.language}")
    prompt = f"Generate an astrological analysis for a person born on {data.dob}"
    if data.time:
        prompt += f" at {data.time}"
    if data.location:
        prompt += f" in {data.location}"
    prompt += f". Include Rashi, Nakshatra, Lagna, daily prediction, weekly prediction, and a life summary. Respond in {data.language}."
    result = await query_openai_text(prompt)
    return {
        "status": "success",
        "rashifal": result
    }

@app.get("/muhurat")
async def get_muhurat(language: Optional[str] = "English"):
    logger.info(f"Muhurat request in language: {language}")
    prompt = f"Give today's muhurat and lucky time suggestions for business, travel, and health. Respond in {language}."
    result = await query_openai_text(prompt)
    return {
        "status": "success",
        "summary": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

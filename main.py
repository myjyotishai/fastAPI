
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import openai
from openai import OpenAI
import os

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
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RashifalRequest(BaseModel):
    dob: str
    time: Optional[str] = None
    location: Optional[str] = None
    

async def query_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert astrologer providing spiritual and astrological guidance."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from OpenAI: {str(e)}"


@app.post("/upload/palm")
async def upload_palm(file: UploadFile = File(...)):
    # Dummy prompt (replace with actual analysis later)
    prompt = "Analyze the palm lines: Life line is long and curved, heart line is deep and straight, head line joins life line, fate line starts from center."
    result = await query_openai(prompt)
    return {
        "status": "success",
        "summary": result
    }

@app.post("/upload/face")
async def upload_face(file: UploadFile = File(...)):
    # Dummy prompt (replace with actual analysis later)
    prompt = "Analyze the face: forehead is broad, eyes are sharp, chin is rounded."
    result = await query_openai(prompt)
    return {
        "status": "success",
        "summary": result
    }

@app.post("/rashifal")
async def get_rashifal(data: RashifalRequest):
    prompt = f"Generate an astrological analysis for a person born on {data.dob}"
    if data.time:
        prompt += f" at {data.time}"
    if data.location:
        prompt += f" in {data.location}"
    prompt += ". Include Rashi, Nakshatra, Lagna, daily prediction, weekly prediction, and a life summary."

    result = await query_openai(prompt)
    return {
        "status": "success",
        "rashifal": result
    }

@app.get("/muhurat")
async def get_muhurat():
    prompt = "Give today's muhurat and lucky time suggestions for business, travel, and health."
    result = await query_openai(prompt)
    return {
        "status": "success",
        "summary": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

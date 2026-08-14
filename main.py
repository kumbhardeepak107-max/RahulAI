from fastapi import FastAPI, UploadFile, File, Form
from google import genai
from brain import get_answer
import os

app = FastAPI()


# Gemini API key Render Environment Variables se
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"


@app.get("/")
def home():
    return {
        "message": "Rahul AI API chal rahi hai!"
    }


@app.post("/chat")
async def chat(data: dict):

    message = data.get("message", "").strip()

    if not message:
        return {
            "reply": "Dost, apna question likho."
        }

    try:

        # Brain.py message ko handle karega
        answer = get_answer(message)

        return {
            "reply": answer
        }

    except Exception as e:

        print("Chat Error:", e)

        return {
            "reply": f"AI Error: {str(e)}"
        }


@app.post("/chat-image")
async def chat_image(
    image: UploadFile = File(...),
    message: str = Form("")
):

    try:

        image_bytes = await image.read()

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                {
                    "inline_data": {
                        "mime_type": image.content_type,
                        "data": image_bytes
                    }
                },
                message if message else "Is photo ko describe karo."
            ]
        )

        return {
            "reply": response.text
        }

    except Exception as e:

        print("Image AI Error:", e)

        return {
            "reply": f"Image AI Error: {str(e)}"
        }

from fastapi import FastAPI, UploadFile, File, Form
from google import genai
from memory import save_memory, get_memory
import os

app = FastAPI()

# Gemini API key
# Yahan apni Gemini API key rakho.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")

client = genai.Client(api_key=API_KEY)

# Current Gemini model
MODEL = "gemini-3.6-flash"


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

    # Naam yaad rakhna
    lower = message.lower()

    if lower.startswith("mera naam "):

        name = message[len("mera naam "):].strip()

        if name:
            save_memory("name", name)

            return {
                "reply": f"Theek hai, main yaad rakhunga ki tumhara naam {name} hai."
            }

    # Naam yaad hai?
    if lower in [
        "mera naam kya hai",
        "mera naam kya he",
        "what is my name"
    ]:

        name = get_memory("name")

        if name:
            return {
                "reply": f"Tumhara naam {name} hai."
            }

        return {
            "reply": "Mujhe abhi tumhara naam yaad nahi hai."
        }

    # Gemini AI
    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=message
        )

        return {
            "reply": response.text
        }

    except Exception as e:

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

        # Gemini ko image + question bhejna
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

        return {
            "reply": f"Image AI Error: {str(e)}"
        }

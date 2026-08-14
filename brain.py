from google import genai
from memory import save_memory, get_memory
import os


# Gemini API key Render ke Environment Variables se aayegi
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.7-flash"


def get_answer(message):
    message = message.strip()
    message_lower = message.lower().strip(" ?!.")


    # Rahul AI ka naam
    if message_lower in [
        "tumhara naam kya hai",
        "tumhara naam kya he",
        "aapka naam kya hai",
        "aapka naam kya he",
        "what is your name",
        "who are you",
        "rahul ai ka naam kya hai"
    ]:
        return "Mera naam Rahul AI hai. Main tumhara AI assistant hoon."


    # User ka naam batana
    if message_lower in [
        "mera naam kya hai",
        "mera naam kya he",
        "what is my name"
    ]:

        name = get_memory("name")

        if name:
            return f"Tumhara naam {name} hai."

        return "Dost, mujhe abhi tumhara naam yaad nahi hai."


    # User ka naam save karna
    if message_lower.startswith("mera naam "):

        name = message[len("mera naam "):].strip()

        # Agar naam ke end me "hai" ho to remove karo
        if name.lower().endswith(" hai"):
            name = name[:-4].strip()

        if name:
            save_memory("name", name)

            return (
                f"Theek hai dost, main yaad rakhunga "
                f"ki tumhara naam {name} hai."
            )


    # Gemini AI
    try:

        prompt = f"""
Tum Rahul AI ho.

Tumhara naam Rahul AI hai.
Tum ek friendly AI assistant ho.

User se natural Hindi/Hinglish me baat karo.
User ko simple language me samjhao.
Apne aap ko Google Gemini mat bolo.
Agar user tumhara naam puche to Rahul AI bolo.

User ka message:
{message}
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if response.text:
            return response.text

        return "Dost, AI ne koi answer nahi diya."


    except Exception as e:

        print("Gemini Error:", e)

        return f"AI Error: {str(e)}"


def image_answer(message, image_bytes, mime_type):

    try:

        prompt = f"""
Tum Rahul AI ho.
Tumhara naam Rahul AI hai.
Tum ek friendly AI assistant ho.

User ne ek photo bheji hai.
Photo ko samajhkar simple Hindi/Hinglish me answer do.

User ka question:
{message if message else "Is photo ko describe karo."}
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_bytes
                    }
                },
                prompt
            ]
        )

        if response.text:
            return response.text

        return "Dost, photo ke baare me answer nahi mil saka."


    except Exception as e:

        print("Gemini Image Error:", e)

        return f"Image AI Error: {str(e)}"  

from google import genai
from memory import save_memory, get_memory
import os


# Gemini API key environment variable se
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")


client = genai.Client(api_key=API_KEY)

# Gemini model
MODEL = "gemini-3.6-flash"


def get_answer(message):
    message_lower = message.lower().strip()

    # -------------------------
    # Naam save karna
    # -------------------------
    if message_lower.startswith("mera naam "):

        name = message[len("mera naam "):].strip()

        if name:
            save_memory("name", name)

            return (
                f"Theek hai, main yaad rakhunga "
                f"ki tumhara naam {name} hai."
            )


    # -------------------------
    # Naam puchna
    # -------------------------
    if message_lower in [
        "mera naam kya hai",
        "mera naam kya he",
        "what is my name"
    ]:

        name = get_memory("name")

        if name:
            return f"Tumhara naam {name} hai."

        return "Mujhe abhi tumhara naam yaad nahi hai."


    # -------------------------
    # Gemini AI
    # -------------------------
    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=message
        )

        if response.text:
            return response.text

        return "AI ne koi answer nahi diya."


    except Exception as e:

        print("Gemini Error:", e)

        return f"AI Error: {str(e)}"


# -------------------------
# Image question
# -------------------------
def image_answer(message):

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=message
        )

        if response.text:
            return response.text

        return "AI ne photo ka koi answer nahi diya."


    except Exception as e:

        print("Image AI Error:", e)

        return f"Image AI Error: {str(e)}"

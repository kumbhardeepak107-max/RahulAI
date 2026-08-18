from google import genai
from memory import save_memory, get_memory, get_all_memory
import os
import time
import random


# =========================================================
# GEMINI SETUP
# =========================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY set nahi hai.")

client = genai.Client(api_key=API_KEY)

# Agar tumhare account me ye model available nahi hai,
# apne available Gemini Flash model ka naam yahan rakho.
MODEL = "gemini-2.5-flash"


# =========================================================
# GEMINI RETRY SYSTEM
# =========================================================

def generate_with_retry(contents, max_attempts=3):

    last_error = None

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=contents
            )

            return response

        except Exception as e:

            last_error = e
            error_text = str(e).upper()

            temporary_error = (
                "503" in error_text
                or "429" in error_text
                or "500" in error_text
                or "502" in error_text
                or "504" in error_text
                or "UNAVAILABLE" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "TIMEOUT" in error_text
            )

            if not temporary_error:
                raise e

            if attempt == max_attempts - 1:
                raise e

            wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)

            print(
                f"Gemini temporary error. "
                f"Retry {attempt + 1}/{max_attempts - 1} "
                f"after {wait_time:.1f}s"
            )

            time.sleep(wait_time)

    raise last_error


# =========================================================
# MEMORY HELPERS
# =========================================================

def get_memory_context():

    try:

        memory = get_all_memory()

        if not memory:
            return "Abhi user ke baare mein koi extra memory nahi hai."

        lines = []

        for key, value in memory.items():

            lines.append(
                f"{key}: {value}"
            )

        return "\n".join(lines)

    except Exception as e:

        print("Memory read error:", e)

        return "Memory available nahi hai."


# =========================================================
# SIMPLE MEMORY DETECTION
# =========================================================

def remember_user_information(message):

    text = message.strip()
    lower = text.lower()

    # -----------------------------------------
    # NAME
    # -----------------------------------------

    if lower.startswith("mera naam "):

        name = text[len("mera naam "):].strip()

        if name.lower().endswith(" hai"):
            name = name[:-4].strip()

        if name:

            save_memory("name", name)

            return (
                f"Theek hai dost, main yaad rakhunga "
                f"ki tumhara naam {name} hai."
            )

    # -----------------------------------------
    # FAVOURITE
    # -----------------------------------------

    favourite_prefixes = [
        "mujhe ",
        "mera favourite ",
        "meri favourite "
    ]

    # Example:
    # Mujhe cricket pasand hai
    if lower.startswith("mujhe ") and " pasand" in lower:

        try:

            value = text[6:]

            if " pasand" in value.lower():

                value = value.lower().split(
                    " pasand"
                )[0].strip()

                if value:

                    save_memory(
                        "preference",
                        value
                    )

                    return (
                        f"Theek hai dost ❤️ "
                        f"main yaad rakhunga ki tumhe "
                        f"{value} pasand hai."
                    )

        except Exception as e:

            print("Preference memory error:", e)

    return None


# =========================================================
# GET USER NAME
# =========================================================

def get_user_name():

    try:

        return get_memory("name")

    except Exception:

        return None


# =========================================================
# MAIN TEXT AI
# =========================================================

def get_answer(message):

    message = message.strip()

    if not message:

        return "Dost, apna question likho."


    message_lower = message.lower().strip(" ?!.")


    # =====================================================
    # RAHUL AI NAME
    # =====================================================

    if message_lower in [
        "tumhara naam kya hai",
        "tumhara naam kya he",
        "aapka naam kya hai",
        "aapka naam kya he",
        "what is your name",
        "who are you",
        "rahul ai ka naam kya hai"
    ]:

        return (
            "Mera naam Rahul AI hai 🤖. "
            "Main tumhara friendly AI assistant hoon."
        )


    # =====================================================
    # USER NAME
    # =====================================================

    if message_lower in [
        "mera naam kya hai",
        "mera naam kya he",
        "what is my name"
    ]:

        name = get_user_name()

        if name:

            return f"Tumhara naam {name} hai ❤️."

        return (
            "Dost, mujhe abhi tumhara naam yaad nahi hai."
        )


    # =====================================================
    # USER INFORMATION REMEMBER
    # =====================================================

    memory_reply = remember_user_information(message)

    if memory_reply:

        return memory_reply


    # =====================================================
    # MEMORY QUESTION
    # =====================================================

    if message_lower in [
        "tumhe mere baare mein kya yaad hai",
        "mujhe mere baare mein kya yaad hai",
        "what do you remember about me"
    ]:

        memory_context = get_memory_context()

        return (
            "Dost, mujhe tumhare baare mein ye yaad hai:\n\n"
            + memory_context
        )


    # =====================================================
    # GEMINI AI
    # =====================================================

    try:

        memory_context = get_memory_context()

        prompt = f"""
Tum Rahul AI ho 🤖.

Tumhara naam Rahul AI hai.

Tum ek friendly, helpful aur intelligent AI assistant ho.

User se natural Hindi/Hinglish mein baat karo.

User ko simple language mein samjhao.

Agar user Hindi mein baat kare to Hindi/Hinglish mein answer do.

Agar user English mein baat kare to English ya simple Hinglish mein answer do.

Apne aap ko Google Gemini mat bolo.

Kabhi bhi ye mat bolo ki tum Google Gemini ho.

User ki saved memory ko context ke roop mein use karo.

User memory:
{memory_context}

Important:
- Agar memory mein user ka naam hai, zarurat ke hisaab se naam use kar sakte ho.
- Memory ko bina zarurat baar-baar repeat mat karo.
- Agar memory mein answer nahi hai to guess mat karo.
- Friendly aur natural raho.
- Dangerous ya unsafe requests mein safe response do.

User ka message:
{message}
"""

        response = generate_with_retry(prompt)

        if response and response.text:

            return response.text.strip()

        return (
            "Dost, AI ne abhi koi answer nahi diya."
        )


    except Exception as e:

        print("Gemini Error:", e)

        error_text = str(e)

        upper_error = error_text.upper()

        if (
            "503" in upper_error
            or "UNAVAILABLE" in upper_error
        ):

            return (
                "Dost, AI server abhi busy hai 😅. "
                "Thodi der baad dobara try karo."
            )

        if (
            "429" in upper_error
            or "RESOURCE_EXHAUSTED" in upper_error
        ):

            return (
                "Dost, AI ki request limit abhi "
                "temporarily full hai. Thodi der baad "
                "dobara try karo."
            )

        if "TIMEOUT" in upper_error:

            return (
                "Dost, server se response aane mein "
                "zyada time lag gaya. Dobara try karo."
            )

        return f"AI Error: {error_text}"


# =========================================================
# IMAGE AI
# =========================================================

def image_answer(message, image_bytes, mime_type):

    try:

        user_question = (
            message.strip()
            if message and message.strip()
            else "Is photo ko simple Hindi mein describe karo."
        )

        memory_context = get_memory_context()

        prompt = f"""
Tum Rahul AI ho 🤖.

Tumhara naam Rahul AI hai.

Tum ek friendly AI assistant ho.

User ne ek photo bheji hai.

Photo ko carefully samjho aur user ke question ka
simple Hindi/Hinglish mein answer do.

Agar photo mein text hai to use padhne ki koshish karo.

Agar tumhe photo mein koi information clearly
dikhai nahi deti, to guess mat karo.

User memory:
{memory_context}

User ka question:
{user_question}
"""

        contents = [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
            },
            prompt
        ]

        response = generate_with_retry(contents)

        if response and response.text:

            return response.text.strip()

        return (
            "Dost, photo ke baare mein answer nahi mil saka."
        )


    except Exception as e:

        print("Gemini Image Error:", e)

        error_text = str(e)

        upper_error = error_text.upper()

        if (
            "503" in upper_error
            or "UNAVAILABLE" in upper_error
        ):

            return (
                "Dost, image AI server abhi busy hai 😅. "
                "Thodi der baad dobara try karo."
            )

        if (
            "429" in upper_error
            or "RESOURCE_EXHAUSTED" in upper_error
        ):

            return (
                "Dost, image AI ki request limit "
                "temporarily full hai. Baad mein try karo."
            )

        if "TIMEOUT" in upper_error:

            return (
                "Dost, photo process hone mein "
                "zyada time lag gaya. Dobara try karo."
            )

        return f"Image AI Error: {error_text}"

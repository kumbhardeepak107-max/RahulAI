from memory import save_memory, get_memory

def get_answer(message):
    text = message.lower().strip()

    if text.startswith("mera naam "):
        name = message.replace("mera naam ", "", 1).strip()
        save_memory("name", name)
        return f"Theek hai, main yaad rakhunga ki tumhara naam {name} hai."

    elif text == "mera naam kya hai":
        name = get_memory("name")
        if name:
            return f"Tumhara naam {name} hai."
        else:
            return "Tumne abhi tak apna naam nahi bataya."

    elif "hello" in text or "hi" in text:
        return "Hello dost! Main Rahul AI hoon."

    elif "kaise ho" in text:
        return "Main bilkul theek hoon. Tum kaise ho?"

    elif "bye" in text:
        return "Bye dost!"

    else:
        return "Mujhe abhi iska jawab nahi pata." 

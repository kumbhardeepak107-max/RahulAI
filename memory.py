import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:
        return {}


def save_memory(key, value):
    memory = load_memory()

    memory[key] = value

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=4)


def get_memory(key):
    memory = load_memory()

    return memory.get(key)

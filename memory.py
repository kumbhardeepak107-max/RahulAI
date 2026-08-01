memory = {}

def save_memory(key, value):
    memory[key] = value

def get_memory(key):
    return memory.get(key, None)

from fastapi import FastAPI
from pydantic import BaseModel
from brain import get_answer

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Rahul AI API chal rahi hai!"}

@app.post("/chat")
def chat(data: ChatRequest):
    reply = get_answer(data.message)
    return {"reply": reply}

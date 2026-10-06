from fastapi import FastAPI
from src.models.schemas import ChatRequest, ChatResponse
from src.services.llm import rylanor_brain

app = FastAPI(title="Rylanor API")

@app.get("/")
async def health_check():
    return {"status": "Rylanor is online"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    ai_reply, action = await rylanor_brain.process_message(request.user_id, request.message)
    
    return ChatResponse(
        reply_text=ai_reply,
        action=action 
    )
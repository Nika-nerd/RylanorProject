from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ActionIntent(BaseModel):
    action_type: str 
    parameters: Dict[str, Any] 

class ChatResponse(BaseModel):
    reply_text: str
    action: Optional[ActionIntent] = None 

from pydantic import BaseModel
from typing import Optional
import nonebot.adapters.qqguild import model

class Channel(BaseModel):
    id: Optional[int] = None
    guild_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None
    owner_id: Optional[int] = None
    private_type: Optional[int] = None
    speak_permission: Optional[int] = None
    application_id: Optional[str] = None
    
    
nonebot.
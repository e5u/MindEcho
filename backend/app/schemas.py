from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Message schemas
class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    emotion: Optional[str] = None
    emotion_score: Optional[float] = None
    is_crisis: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# Conversation schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationOut(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationOut):
    messages: List[MessageOut] = []


# Chat schemas
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    user_message: MessageOut
    assistant_message: MessageOut
    is_crisis: bool = False
    crisis_message: Optional[str] = None
    processor_time: Optional[float] = None  # 处理时间（秒）


# Emotion schemas
class EmotionRecordOut(BaseModel):
    id: int
    emotion: str
    emotion_score: float
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmotionStats(BaseModel):
    emotion: str
    count: int
    percentage: float


class EmotionHistoryResponse(BaseModel):
    records: List[EmotionRecordOut]
    stats: List[EmotionStats]
    total: int


class QuickMoodInput(BaseModel):
    mood: str
    note: Optional[str] = None


class QuickMoodResponse(BaseModel):
    emotion: str
    emotion_label: str
    micro_support: str
    breathing_guide: Optional[str] = None


class WeeklyReportResponse(BaseModel):
    period: str
    emotional_trend: str
    possible_causes: List[str]
    suggestions: List[str]
    note: str


class DailySuggestionResponse(BaseModel):
    date: str
    memory_hint: str
    suggestions: List[str]


class CbtGuidanceRequest(BaseModel):
    thought: str
    emotion: Optional[str] = None


class CbtGuidanceResponse(BaseModel):
    intro: str
    questions: List[str]

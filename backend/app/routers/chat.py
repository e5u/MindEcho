from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.emotion_service import detect_emotion, detect_crisis
from app.services.ai_service import get_ai_response
import asyncio

router = APIRouter(prefix="/api/chat", tags=["对话"])


@router.post("/send", response_model=schemas.ChatResponse)
async def send_message(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """发送消息并获取AI回复"""
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == request.conversation_id,
            models.Conversation.user_id == current_user.id,
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
    else:
        # Create new conversation with first message as title
        title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        conversation = models.Conversation(
            user_id=current_user.id,
            title=title,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Detect emotion and crisis
    emotion, emotion_score = detect_emotion(request.message)
    is_crisis = detect_crisis(request.message)
    
    # Save user message
    user_msg = models.Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        emotion=emotion,
        emotion_score=emotion_score,
        is_crisis=1 if is_crisis else 0,
    )
    db.add(user_msg)
    
    # Save emotion record
    emotion_record = models.EmotionRecord(
        user_id=current_user.id,
        emotion=emotion,
        emotion_score=emotion_score,
    )
    db.add(emotion_record)
    db.commit()
    db.refresh(user_msg)
    
    # Get conversation history
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation.messages
    ]
    
    # Get AI response
    ai_response_text = await get_ai_response(
        user_message=request.message,
        emotion=emotion,
        conversation_history=history,
        is_crisis=is_crisis,
    )
    
    # Save assistant message
    assistant_msg = models.Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    
    return {
        "conversation_id": conversation.id,
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "is_crisis": is_crisis,
        "crisis_message": "请立即拨打心理援助热线：400-161-9995" if is_crisis else None,
    }


@router.get("/conversations", response_model=List[schemas.ConversationOut])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """获取用户所有对话列表"""
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == current_user.id
    ).order_by(models.Conversation.updated_at.desc(), models.Conversation.created_at.desc()).all()
    return conversations


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """获取特定对话及其消息"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == current_user.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """删除对话"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == current_user.id,
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).delete()
    db.delete(conversation)
    db.commit()
    return {"message": "对话已删除"}

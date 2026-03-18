from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.emotion_service import EMOTION_LABELS

router = APIRouter(prefix="/api/emotions", tags=["情绪"])


@router.get("/history", response_model=schemas.EmotionHistoryResponse)
def get_emotion_history(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """获取情绪历史记录"""
    since = datetime.utcnow() - timedelta(days=days)
    
    records = db.query(models.EmotionRecord).filter(
        models.EmotionRecord.user_id == current_user.id,
        models.EmotionRecord.created_at >= since,
    ).order_by(models.EmotionRecord.created_at.desc()).limit(200).all()
    
    # Calculate stats
    total = len(records)
    emotion_counts = {}
    for record in records:
        emotion_counts[record.emotion] = emotion_counts.get(record.emotion, 0) + 1
    
    stats = []
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
        stats.append(schemas.EmotionStats(
            emotion=emotion,
            count=count,
            percentage=round(count / total * 100, 1) if total > 0 else 0,
        ))
    
    return {
        "records": records,
        "stats": stats,
        "total": total,
    }


@router.get("/trend")
def get_emotion_trend(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """获取情绪趋势数据（按天分组）"""
    since = datetime.utcnow() - timedelta(days=days)
    
    records = db.query(models.EmotionRecord).filter(
        models.EmotionRecord.user_id == current_user.id,
        models.EmotionRecord.created_at >= since,
    ).order_by(models.EmotionRecord.created_at.asc()).all()
    
    # Group by date
    daily_data = {}
    for record in records:
        date_str = record.created_at.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {}
        emotion = record.emotion
        daily_data[date_str][emotion] = daily_data[date_str].get(emotion, 0) + 1
    
    # Fill missing dates
    result = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        result.append({
            "date": date,
            "emotions": daily_data.get(date, {}),
        })
    
    return {"trend": result, "labels": EMOTION_LABELS}

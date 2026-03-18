from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.emotion_service import EMOTION_LABELS
from app.services.report_service import generate_weekly_report
from app.services.memory_service import rebuild_user_memory, build_daily_suggestions, should_rebuild_memory

router = APIRouter(prefix="/api/emotions", tags=["情绪"])

QUICK_MOOD_MAPPING = {
    "stress": ("anxious", 0.78, "先把双脚踩稳地面，跟我做3轮呼吸：吸气4秒，呼气6秒。你已经在照顾自己了。"),
    "sad": ("sad", 0.75, "你愿意表达难受已经很勇敢。现在给自己一个小目标：喝几口温水，慢慢把身体放松下来。"),
    "angry": ("angry", 0.8, "生气时先暂停10秒，把注意力放在呼吸上，再决定下一步。你的感受值得被看见。"),
}


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


@router.post("/quick-checkin", response_model=schemas.QuickMoodResponse)
def quick_mood_checkin(
    request: schemas.QuickMoodInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """一键情绪输入并返回即时微支持"""
    mood_key = request.mood.lower().strip()
    if mood_key not in QUICK_MOOD_MAPPING:
        mood_key = "stress"

    emotion, score, support = QUICK_MOOD_MAPPING[mood_key]
    record = models.EmotionRecord(
        user_id=current_user.id,
        emotion=emotion,
        emotion_score=score,
        note=request.note,
    )
    db.add(record)
    db.commit()
    profile = db.query(models.UserMemory).filter(models.UserMemory.user_id == current_user.id).first()
    if should_rebuild_memory(profile):
        profile = rebuild_user_memory(db, current_user.id)

    return {
        "emotion": emotion,
        "emotion_label": EMOTION_LABELS.get(emotion, "平静"),
        "micro_support": support,
        "breathing_guide": "吸气4秒 → 停2秒 → 呼气6秒，重复3次。",
    }


@router.get("/weekly-report", response_model=schemas.WeeklyReportResponse)
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """生成近7天AI心理周报"""
    return generate_weekly_report(db, current_user.id)


@router.get("/daily-suggestion", response_model=schemas.DailySuggestionResponse)
def get_daily_suggestion(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """基于历史情绪和使用行为生成个性化建议"""
    profile = db.query(models.UserMemory).filter(models.UserMemory.user_id == current_user.id).first()
    if should_rebuild_memory(profile):
        profile = rebuild_user_memory(db, current_user.id)
    recent_records = db.query(models.EmotionRecord).filter(
        models.EmotionRecord.user_id == current_user.id
    ).order_by(models.EmotionRecord.created_at.desc()).limit(10).all()

    suggestions = build_daily_suggestions(profile, [record.emotion for record in recent_records])
    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "memory_hint": profile.conversation_summary or "今天继续温柔地照顾自己。",
        "suggestions": suggestions,
    }

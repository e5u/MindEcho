from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from app import models


TREND_TEXT = {
    "positive": "过去7天整体情绪逐步回稳，积极情绪有所增加。",
    "negative": "过去7天负面情绪偏多，最近几天压力感有上升趋势。",
    "mixed": "过去7天情绪有波动，存在起伏但也出现了恢复时段。",
}

NEGATIVE_TREND_MULTIPLIER = 1.3
POSITIVE_TREND_MULTIPLIER = 1.1


CAUSE_HINTS = {
    "anxious": "学习任务、考试或未来规划带来的不确定感可能是主要诱因。",
    "sad": "人际关系、期待落差或持续疲惫可能让情绪更低落。",
    "angry": "近期边界被打破或沟通不顺，可能引发了较多愤怒感受。",
    "lonely": "社交连接不足或缺乏被理解感，可能加重孤独体验。",
}


def generate_weekly_report(db: Session, user_id: int) -> Dict[str, object]:
    since = datetime.utcnow() - timedelta(days=7)
    records = db.query(models.EmotionRecord).filter(
        models.EmotionRecord.user_id == user_id,
        models.EmotionRecord.created_at >= since,
    ).order_by(models.EmotionRecord.created_at.asc()).all()

    if not records:
        return {
            "period": "近7天",
            "emotional_trend": "近7天记录较少，暂时无法判断稳定趋势。",
            "possible_causes": ["最近可能较忙，尚未形成稳定记录习惯。"],
            "suggestions": ["每天用30秒记录一次心情，连续一周后可获得更准确分析。"],
            "note": "这是一份辅助理解情绪的AI周报，不替代专业心理评估。",
        }

    counter = Counter(record.emotion for record in records)
    negative_total = sum(counter.get(e, 0) for e in ["sad", "anxious", "angry", "lonely", "fear"])
    positive_total = counter.get("happy", 0) + counter.get("neutral", 0)

    if negative_total > positive_total * NEGATIVE_TREND_MULTIPLIER:
        trend_key = "negative"
    elif positive_total > negative_total * POSITIVE_TREND_MULTIPLIER:
        trend_key = "positive"
    else:
        trend_key = "mixed"

    top_negative = [emo for emo, _ in counter.most_common() if emo in CAUSE_HINTS][:2]
    causes: List[str] = [CAUSE_HINTS[e] for e in top_negative if e in CAUSE_HINTS] or ["近期情绪波动可能与学业节奏和休息不足有关。"]

    suggestions = [
        "把今天最困扰你的念头写成一句话，再问自己：有没有证据支持/反驳它？",
        "把学习任务拆成25分钟的小块，完成一块后给自己一个短休息。",
        "每晚睡前写下1件完成的小事，帮助大脑看到“我在前进”。",
    ]
    return {
        "period": "近7天",
        "emotional_trend": TREND_TEXT[trend_key],
        "possible_causes": causes,
        "suggestions": suggestions,
        "note": "这是一份辅助理解情绪的AI周报，不替代专业心理评估。",
    }

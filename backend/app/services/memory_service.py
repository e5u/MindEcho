from collections import Counter
from typing import Dict, List
from sqlalchemy.orm import Session
from app import models


STRESS_HINTS = ["压力", "ddl", "截止", "作业", "考试", "绩点"]
ANXIETY_HINTS = ["焦虑", "担心", "害怕", "紧张", "睡不着"]
HABIT_HINTS = ["熬夜", "失眠", "刷手机", "拖延", "暴饮暴食"]


def _level_by_ratio(ratio: float) -> str:
    if ratio >= 0.6:
        return "high"
    if ratio >= 0.3:
        return "medium"
    return "low"


def rebuild_user_memory(db: Session, user_id: int) -> models.UserMemory:
    records = db.query(models.EmotionRecord).filter(
        models.EmotionRecord.user_id == user_id
    ).order_by(models.EmotionRecord.created_at.desc()).limit(60).all()

    messages = db.query(models.Message).join(
        models.Conversation, models.Message.conversation_id == models.Conversation.id
    ).filter(
        models.Conversation.user_id == user_id,
        models.Message.role == "user",
    ).order_by(models.Message.created_at.desc()).limit(30).all()

    total_messages = max(len(messages), 1)
    all_text = " ".join(msg.content for msg in messages)
    stress_ratio = sum(1 for k in STRESS_HINTS if k in all_text) / max(len(STRESS_HINTS), 1)
    anxiety_ratio = sum(1 for k in ANXIETY_HINTS if k in all_text) / max(len(ANXIETY_HINTS), 1)
    habit_hits = [hint for hint in HABIT_HINTS if hint in all_text]

    emotion_counter = Counter(record.emotion for record in records)
    top_emotions = [emotion for emotion, _ in emotion_counter.most_common(3)]
    summary = "、".join(top_emotions) if top_emotions else "平静"

    stress_level = _level_by_ratio(stress_ratio)
    anxiety_level = _level_by_ratio(anxiety_ratio)
    habit_pattern = "、".join(habit_hits) if habit_hits else "暂未发现明显习惯模式"

    profile = db.query(models.UserMemory).filter(models.UserMemory.user_id == user_id).first()
    if not profile:
        profile = models.UserMemory(user_id=user_id)
        db.add(profile)

    profile.stress_pattern = stress_level
    profile.anxiety_pattern = anxiety_level
    profile.habit_pattern = habit_pattern
    profile.top_emotions = ",".join(top_emotions)
    profile.conversation_summary = (
        f"最近{min(len(messages), total_messages)}次表达以{summary}为主，"
        f"压力水平{stress_level}，焦虑水平{anxiety_level}。"
    )
    db.commit()
    db.refresh(profile)
    return profile


def get_memory_context(profile: models.UserMemory | None) -> Dict[str, str]:
    if not profile:
        return {
            "stress_pattern": "unknown",
            "anxiety_pattern": "unknown",
            "habit_pattern": "暂无",
            "conversation_summary": "暂无历史对话记忆。",
        }

    return {
        "stress_pattern": profile.stress_pattern,
        "anxiety_pattern": profile.anxiety_pattern,
        "habit_pattern": profile.habit_pattern or "暂无",
        "conversation_summary": profile.conversation_summary or "暂无历史对话记忆。",
    }


def build_daily_suggestions(profile: models.UserMemory | None, recent_emotions: List[str]) -> List[str]:
    suggestions: List[str] = []
    if profile and profile.stress_pattern in {"high", "medium"}:
        suggestions.append("今天安排一次3分钟呼吸练习：吸气4秒-停2秒-呼气6秒，循环5次。")
    if profile and profile.anxiety_pattern in {"high", "medium"}:
        suggestions.append("尝试写下“我最担心什么、最坏会怎样、我能做什么”三行笔记，帮助思绪落地。")
    if any(e in {"sad", "lonely"} for e in recent_emotions):
        suggestions.append("给一位信任的同学或朋友发一条问候，建立一点连接感。")
    if not suggestions:
        suggestions.append("你今天整体状态较稳定，可以记录一件让你有力量的小事。")
    return suggestions[:3]

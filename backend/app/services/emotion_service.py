import re
from typing import Tuple

# Emotion keyword mappings (Chinese)
EMOTION_KEYWORDS = {
    "happy": [
        "开心", "快乐", "高兴", "愉快", "幸福", "喜悦", "兴奋", "欢喜", "美好", "棒极了",
        "太好了", "开怀", "畅快", "满意", "满足", "愉悦", "舒心", "轻松", "心情好", "笑"
    ],
    "sad": [
        "难过", "伤心", "悲伤", "痛苦", "委屈", "哭", "流泪", "心疼", "失落", "沮丧",
        "郁闷", "悲痛", "忧伤", "心碎", "绝望", "无助", "消沉", "悲观", "低落", "不开心"
    ],
    "anxious": [
        "焦虑", "担心", "紧张", "不安", "忧虑", "烦躁", "着急", "慌张", "害怕失败", "压力",
        "压迫", "压抑", "不知所措", "慌乱", "心慌", "惶恐", "彷徨", "迷茫", "困惑", "焦躁"
    ],
    "angry": [
        "愤怒", "生气", "气愤", "恼火", "发火", "暴怒", "愤恨", "气死", "烦透了", "讨厌",
        "憎恨", "厌恶", "恼怒", "怒火", "暴躁", "激动", "气不过", "窝火", "火大", "怒"
    ],
    "fear": [
        "害怕", "恐惧", "恐慌", "惊吓", "惊恐", "怕", "畏惧", "战栗", "颤抖", "惊吓",
        "胆怯", "惊慌", "恐慌", "惧怕", "不敢", "担惊受怕"
    ],
    "lonely": [
        "孤独", "孤单", "寂寞", "无聊", "没人陪", "一个人", "孤立", "被孤立", "没朋友",
        "没有人", "独自", "落单", "被遗忘", "被忽视", "冷落", "疏远"
    ],
}

# Crisis keywords - self-harm signals
CRISIS_KEYWORDS = [
    "自杀", "轻生", "不想活", "活不下去", "死了算了", "结束生命", "了结", "去死",
    "自残", "割腕", "伤害自己", "想死", "没意义活", "不如死", "寻死",
    "跳楼", "跳桥", "吃药死", "上吊", "活着没意思", "活着没有意义",
    "不想存在", "消失算了", "人间不值得"
]


def detect_emotion(text: str) -> Tuple[str, float]:
    """Detect primary emotion from text. Returns (emotion, score)."""
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}
    
    text_lower = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[emotion] += 1
    
    max_emotion = max(scores, key=scores.get)
    max_score = scores[max_emotion]
    
    if max_score == 0:
        return "neutral", 0.5
    
    # Normalize score between 0.5 and 1.0
    normalized_score = min(0.5 + (max_score * 0.1), 1.0)
    return max_emotion, normalized_score


def detect_crisis(text: str) -> bool:
    """Detect if text contains crisis/self-harm signals."""
    for keyword in CRISIS_KEYWORDS:
        if keyword in text:
            return True
    return False


EMOTION_LABELS = {
    "happy": "开心",
    "sad": "悲伤",
    "anxious": "焦虑",
    "angry": "愤怒",
    "neutral": "平静",
    "fear": "恐惧",
    "lonely": "孤独",
}

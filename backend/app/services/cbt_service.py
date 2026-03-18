from typing import List


def build_cbt_questions(thought: str, emotion: str | None = None) -> List[str]:
    prefix = "谢谢你愿意说出来。我们可以一起慢慢看这件事。"
    emotion_hint = ""
    if emotion == "anxious":
        emotion_hint = "当焦虑出现时，大脑会自动放大风险。"
    elif emotion == "sad":
        emotion_hint = "当低落时，我们常只看到“做不到”的部分。"
    elif emotion == "angry":
        emotion_hint = "当愤怒时，背后往往也有被忽视或受伤的感受。"

    questions = [
        "这个想法出现时，你脑海里最先闪过的证据是什么？",
        "如果你最信任的朋友遇到同样情况，你会如何描述这件事给TA听？",
        "有没有一种更平衡、对你更有帮助的说法，可以替代原来的想法？",
    ]
    if thought:
        display_thought = thought if len(thought) <= 30 else f"{thought[:30]}…"
        questions.append(f"当你想到“{display_thought}”时，你的情绪从0到10大约是几分？")

    return [prefix, emotion_hint, *questions] if emotion_hint else [prefix, *questions]

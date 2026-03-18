import os
import random
from typing import List, Dict, Optional
from app.services.emotion_service import detect_emotion, detect_crisis, EMOTION_LABELS

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

SYSTEM_PROMPT = """你是MindEcho，一个专为中国大学生设计的心理健康助手。你的角色是温暖、支持性的陪伴者，帮助学生处理情绪和心理困扰。

请遵循以下原则：
1. 始终用中文回复，语气温暖、亲切、不带评判
2. 积极倾听，给予情感支持和认可
3. 在适当时候提供实际建议，但不强迫
4. 如果发现用户有自伤或自杀的迹象，立即提供危机资源
5. 鼓励用户寻求专业心理援助
6. 保持积极、充满希望的态度，但不否认用户的痛苦感受
7. 使用简单易懂的语言，贴近大学生的表达方式

危机资源：
- 北京心理危机研究与干预中心：010-82951332
- 全国心理援助热线：400-161-9995
- 希望24热线：400-161-9995"""

# Fallback responses when OpenAI is not configured
FALLBACK_RESPONSES = {
    "happy": [
        "听到你这么开心，我也替你感到高兴！😊 能分享一下是什么让你这么愉快吗？",
        "你的好心情感染了我！保持这种积极的状态真的很棒。是发生什么好事了吗？",
        "感受到你满满的正能量～ 开心的时候要好好记住这种感觉哦！",
    ],
    "sad": [
        "我能感受到你现在有些难过。没关系，难过是正常的情绪，让自己先好好感受一下。我在这里陪着你。💙",
        "听到你这些，我的心也被触动了。你愿意跟我说说，是什么让你感到这么伤心吗？",
        "有时候，难过的感觉真的很沉重。你不是一个人，我在这里听你说。慢慢来，不用着急。",
    ],
    "anxious": [
        "我理解你现在感到很焦虑，这种感觉确实很不舒服。深呼吸一下——先吸气4秒，屏住2秒，再呼气6秒。试试看？",
        "焦虑的感觉就像乌云压顶，但乌云终究会散去的。你现在最担心的是什么？说出来，也许会好受一些。",
        "感觉到你内心的不安。焦虑往往是因为我们太在乎某件事了。你愿意告诉我是什么让你这么担心吗？",
    ],
    "angry": [
        "感觉你现在情绪很激动，生气是完全正常的反应。能告诉我是什么事让你这么愤怒吗？",
        "我理解你现在很生气。先让自己稍微平静一下，然后我们一起来看看发生了什么？",
        "愤怒背后往往隐藏着受伤的感受。你愿意跟我说说发生了什么吗？我会认真听的。",
    ],
    "fear": [
        "听起来你现在感到很害怕。恐惧的感觉真的很难受，你不用一个人承担这些。我在这里。",
        "我能感受到你内心的恐惧。先深呼吸，提醒自己你现在是安全的。能告诉我让你害怕的是什么吗？",
        "害怕是我们面对威胁时的自然反应。你现在的感受是完全正常的。我们可以一起面对它。",
    ],
    "lonely": [
        "孤独的感觉真的很难受，尤其是在大学这种地方。你不是一个人的，我在这里陪你。💙",
        "有时候即使身处人群中，也会感到孤单。你愿意告诉我，是什么样的孤独感困扰着你吗？",
        "大学生活有时候真的会让人感到很孤独。这种感受是真实的，也是可以改变的。我们来聊聊？",
    ],
    "neutral": [
        "谢谢你愿意和我分享。我在这里，随时都可以倾听你的心声。今天感觉怎么样？",
        "很高兴你来找我聊天。不管是开心还是烦恼，都可以和我说说。你现在有什么想聊的吗？",
        "我在这里陪着你。有什么事情想和我聊聊吗？不管是大事小事，我都会认真听的。",
    ],
}

CRISIS_RESPONSE = """我非常担心你刚才说的话。听起来你现在承受着非常沉重的痛苦，我想让你知道，你的生命对我来说非常重要。

请你现在拨打这些求助热线，专业的老师会帮助你：
📞 **北京心理危机研究与干预中心**：010-82951332
📞 **全国心理援助热线**：400-161-9995  
📞 **希望24热线**：400-161-9995

如果你现在身边有人，请告诉他们你的感受。如果感觉很紧急，请拨打120或前往最近的医院急诊。

你不是一个人，请不要放弃。💙"""


async def get_ai_response(
    user_message: str,
    emotion: str,
    conversation_history: List[Dict],
    is_crisis: bool = False,
) -> str:
    """Get AI response. Uses OpenAI if configured, otherwise uses fallback responses."""
    
    if is_crisis:
        return CRISIS_RESPONSE
    
    # Try OpenAI if configured
    if OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-openai-api-key-here":
        try:
            return await _get_openai_response(user_message, conversation_history)
        except Exception:
            pass
    
    # Use fallback responses
    responses = FALLBACK_RESPONSES.get(emotion, FALLBACK_RESPONSES["neutral"])
    return random.choice(responses)


async def _get_openai_response(
    user_message: str,
    conversation_history: List[Dict],
) -> str:
    """Get response from OpenAI API."""
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history (last 10 messages)
    for msg in conversation_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=500,
        temperature=0.8,
    )
    
    return response.choices[0].message.content

"""
情感分析工具
调用DeepSeek分析单段文本的情感倾向
输出：{"label": "情感标签", "score": 0-1}
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_client import LLMClient


SENTIMENT_PROMPT = """你是一名情感分析专家。请分析以下文本的情感倾向。

要求：
1. 从以下标签中选择最匹配的一个：愤怒、委屈、辩解、焦虑、失望、中立、积极
2. 给出情感强度评分（0-1，0最弱、1最强）
3. 仅输出JSON格式，不要额外文字

输出格式：
{"label": "情感标签", "score": 0.0-1.0}"""


def analyze_sentiment(text: str, llm: LLMClient = None) -> dict:
    """分析单段文本的情感倾向"""
    if not text or not text.strip():
        return {"label": "无内容", "score": 0.0}
    
    if llm is None:
        llm = LLMClient()
    
    messages = [
        {"role": "system", "content": SENTIMENT_PROMPT},
        {"role": "user", "content": text[:1000]}
    ]
    
    result = llm.chat_with_json(messages, fallback={"label": "分析失败", "score": 0.0})
    return result


def analyze_both_sides(plaintiff_claim: str, defendant_defense: str, llm: LLMClient = None) -> dict:
    """同时分析双方情感"""
    if llm is None:
        llm = LLMClient()
    
    prompt = SENTIMENT_PROMPT + "\n\n现在请分析以下两段文本的情感，分别输出：\n" + \
        '{"party_a": {"label": "...", "score": 0.0}, "party_b": {"label": "...", "score": 0.0}}'
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"甲方：{plaintiff_claim[:800]}\n\n乙方：{defendant_defense[:800]}"}
    ]
    
    result = llm.chat_with_json(messages, fallback={
        "party_a": {"label": "分析失败", "score": 0.0},
        "party_b": {"label": "分析失败", "score": 0.0}
    })
    return result


if __name__ == "__main__":
    test_text = "我真的太生气了！明明说好了今天还钱，结果又找借口推脱，这已经是第三次了！"
    result = analyze_sentiment(test_text)
    print(f"情感分析结果: {result}")

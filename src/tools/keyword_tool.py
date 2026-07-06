"""
关键词提取工具
使用jieba的TF-IDF算法提取关键词
输出：[{"word": str, "weight": float}, ...]
"""
import jieba.analyse


def extract_keywords(text: str, top_k: int = 10) -> list:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        top_k: 返回前k个关键词
    
    Returns:
        [{"word": "关键词", "weight": 0.8}, ...]
    """
    if not text or not text.strip():
        return []
    
    # 使用jieba的TF-IDF提取关键词
    keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
    
    result = [{"word": word, "weight": round(weight, 4)} for word, weight in keywords]
    return result


def extract_keywords_both(plaintiff_claim: str, defendant_defense: str, top_k: int = 10) -> dict:
    """
    同时提取双方陈述的关键词
    
    Returns:
        {
            "party_a": [{"word": "...", "weight": 0.0}, ...],
            "party_b": [{"word": "...", "weight": 0.0}, ...],
            "common": ["共同关键词1", ...]   # 双方共有的关键词
        }
    """
    a_words = extract_keywords(plaintiff_claim, top_k)
    b_words = extract_keywords(defendant_defense, top_k)
    
    a_word_set = set(w["word"] for w in a_words)
    b_word_set = set(w["word"] for w in b_words)
    common = list(a_word_set & b_word_set)
    
    return {
        "party_a": a_words,
        "party_b": b_words,
        "common": common
    }


if __name__ == '__main__':
    test_text = "我跟他合租一年了，说好了水电费平摊，但他连续三个月不交，每次催他都找借口。"
    result = extract_keywords(test_text, top_k=5)
    print(f"关键词提取结果: {result}")

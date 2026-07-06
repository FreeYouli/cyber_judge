"""
赛博判官核心编排器
串联：情感分析 → 关键词提取 → 相似案例检索 → LLM综合推理 → 输出判决书
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMClient
from tools.sentiment_tool import analyze_both_sides
from tools.keyword_tool import extract_keywords, extract_keywords_both
from tools.retrieval_tool import create_retriever
from utils.constants import SYSTEM_PROMPT, JUDGMENT_SCHEMA
from utils.config import SIMILARITY_CASES_PATH


class CyberJudge:
    """赛博判官 - 纠纷调解Agent"""
    
    def __init__(self, llm: LLMClient = None, data_path: str = None):
        self.llm = llm or LLMClient()
        
        # 加载检索器
        path = data_path or str(SIMILARITY_CASES_PATH)
        if os.path.exists(path):
            self.retriever = create_retriever(path)
        else:
            print(f"[赛博判官] 警告：案例数据不存在 ({path})，跳过检索")
            self.retriever = None
    
    def judge(self, plaintiff_claim: str, defendant_defense: str, verbose: bool = True) -> dict:
        """执行完整的纠纷判决流程"""
        if verbose:
            print("=" * 50)
            print("⚖️  赛博判官 - 纠纷调解分析")
            print("=" * 50)
        
        # 步骤1：情感分析
        if verbose:
            print("\n[步骤1/4] 情感分析...")
        sentiments = analyze_both_sides(plaintiff_claim, defendant_defense, self.llm)
        if verbose:
            sa = sentiments.get("party_a", {})
            sb = sentiments.get("party_b", {})
            print(f"  甲方情绪：{sa.get('label', '?')} (强度{sa.get('score', 0):.2f})")
            print(f"  乙方情绪：{sb.get('label', '?')} (强度{sb.get('score', 0):.2f})")
        
        # 步骤2：关键词提取
        if verbose:
            print("\n[步骤2/4] 关键词提取...")
        keywords = extract_keywords_both(plaintiff_claim, defendant_defense, top_k=8)
        if verbose:
            print(f"  甲方核心词：{[w['word'] for w in keywords['party_a'][:5]]}")
            print(f"  乙方核心词：{[w['word'] for w in keywords['party_b'][:5]]}")
            print(f"  共同关注点：{keywords['common'][:5]}")
        
        # 步骤3：相似案例检索
        similar_cases = []
        if self.retriever:
            if verbose:
                print("\n[步骤3/4] 相似案例检索...")
            similar_cases = self.retriever.search(
                plaintiff_claim, defendant_defense, top_k=3
            )
            if verbose:
                for c in similar_cases:
                    print(f"  → 相似度{c['similarity']:.3f} | {c['dispute_type']}")
        else:
            if verbose:
                print("\n[步骤3/4] 相似案例检索（跳过，无数据）")
        
        # 步骤4：LLM综合推理
        if verbose:
            print("\n[步骤4/4] LLM综合推理，生成判决书...")
        
        judgment = self._reason(
            plaintiff_claim, defendant_defense, sentiments, keywords, similar_cases
        )
        
        if verbose:
            print("\n" + "=" * 50)
            print("📋 判决书")
            print("=" * 50)
            print(f"案情摘要：{judgment.get('case_summary', '生成失败')}")
            print(f"责任划分：甲方{judgment.get('responsibility_split', {}).get('party_a', '?')}% / 乙方{judgment.get('responsibility_split', {}).get('party_b', '?')}%")
            print(f"和解建议：{judgment.get('suggestions', '生成失败')}")
        
        return judgment
    
    def _reason(self, plaintiff_claim, defendant_defense, sentiments, keywords, similar_cases) -> dict:
        """LLM综合推理，生成判决书"""
        # 构建上下文
        context = self._build_context(
            plaintiff_claim, defendant_defense, sentiments, keywords, similar_cases
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        result = self.llm.chat_with_json(messages, fallback={
            "case_summary": "LLM推理失败，请检查网络或API Key",
            "key_conflicts": [],
            "party_a_sentiment": {"label": "分析失败", "score": 0.0},
            "party_b_sentiment": {"label": "分析失败", "score": 0.0},
            "responsibility_split": {"party_a": 0, "party_b": 0, "description": "无法分析"},
            "fact_finding": "推理失败",
            "suggestions": "推理失败，请重试",
            "radar_scores": {
                "甲方": {"事实清晰度": 0, "逻辑合理性": 0, "态度配合度": 0, "证据充分性": 0, "诉求合理性": 0},
                "乙方": {"事实清晰度": 0, "逻辑合理性": 0, "态度配合度": 0, "证据充分性": 0, "诉求合理性": 0}
            }
        })
        return result
    
    def _build_context(self, plaintiff_claim, defendant_defense, sentiments, keywords, similar_cases) -> str:
        """构建推理上下文"""
        parts = []
        parts.append("=== 甲方陈述 ===")
        parts.append(plaintiff_claim)
        parts.append("\n=== 乙方陈述 ===")
        parts.append(defendant_defense)
        parts.append("\n=== 情感分析结果 ===")
        parts.append(f"甲方情绪：{sentiments.get('party_a', {})}")
        parts.append(f"乙方情绪：{sentiments.get('party_b', {})}")
        parts.append("\n=== 关键词提取 ===")
        parts.append(f"甲方关键词：{[w['word'] for w in keywords.get('party_a', [])[:5]]}")
        parts.append(f"乙方关键词：{[w['word'] for w in keywords.get('party_b', [])[:5]]}")
        parts.append(f"双方共同关注点：{keywords.get('common', [])[:5]}")
        if similar_cases:
            parts.append("\n=== 相似案例参考 ===")
            for i, c in enumerate(similar_cases, 1):
                parts.append(f"案例{i}(相似度{c['similarity']:.2f}): {c['dispute_type']}")
                parts.append(f"  甲方：{c['plaintiff_claim'][:100]}...")
                parts.append(f"  乙方：{c['defendant_defense'][:100]}...")
        parts.append("\n请根据以上信息，严格按照JSON格式输出判决书。")
        return "\n".join(parts)


def create_judge() -> CyberJudge:
    """快捷创建赛博判官实例"""
    return CyberJudge()


if __name__ == "__main__":
    # 测试
    judge = create_judge()
    result = judge.judge(
        "室友总是偷用我的洗发水和护肤品，我放在卫生间的瓶子里明显少了，她还不承认",
        "我只是偶尔借用一下，大家都是室友何必这么计较",
        verbose=True
    )

"""
相似案例检索工具
基于TF-IDF + 余弦相似度，从历史纠纷数据中检索Top-K相似案例
输出：[{"case_index": int, "similarity": float, ...}, ...]
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class CaseRetriever:
    """相似案例检索器"""
    
    def __init__(self, data_path: str = None):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            analyzer="char",
            token_pattern=None
        )
        self.tfidf_matrix = None
        self.cases = None
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, data_path: str):
        """加载数据并建立TF-IDF索引"""
        self.cases = pd.read_csv(data_path, encoding="utf-8-sig")
        combined = (
            self.cases["plaintiff_claim"].fillna("") + " " +
            self.cases["defendant_defense"].fillna("")
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(combined)
        print(f"[检索器] 已加载 {len(self.cases)} 条案例，建立TF-IDF索引")
    
    def search(self, plaintiff_claim: str, defendant_defense: str = "", top_k: int = 3) -> list:
        """检索最相似的案例"""
        if self.tfidf_matrix is None or self.cases is None:
            print("[检索器] 未加载数据，请先调用 load_data()")
            return []
        
        query_text = plaintiff_claim + " " + defendant_defense
        query_vec = self.vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] < 0.01:
                continue
            case = self.cases.iloc[idx]
            results.append({
                "case_index": int(idx),
                "similarity": round(float(similarities[idx]), 4),
                "plaintiff_claim": str(case.get("plaintiff_claim", ""))[:200],
                "defendant_defense": str(case.get("defendant_defense", ""))[:200],
                "dispute_type": case.get("dispute_type", "未知"),
            })
        return results


def create_retriever(data_path: str = None) -> CaseRetriever:
    """快捷创建检索器"""
    if data_path is None:
        data_path = str(Path(__file__).parent.parent.parent / "data" / "cleaned_disputes.csv")
    return CaseRetriever(data_path)


if __name__ == "__main__":
    test_path = Path(__file__).parent.parent.parent / "data" / "cleaned_disputes.csv"
    if test_path.exists():
        retriever = create_retriever(str(test_path))
        result = retriever.search("说好了今天还钱又找借口推脱", "我不是不还只是手头紧", top_k=3)
        print(f"检索结果 ({len(result)}条):")
        for r in result:
            print(f"  相似度{r['similarity']:.3f} | {r['dispute_type']}")
    else:
        print(f"[测试] 数据文件不存在: {test_path}")
        print("请队友A先生成数据后再测试")

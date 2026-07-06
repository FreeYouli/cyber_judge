"""
数据清洗模块
输入：包含 plaintiff_claim, defendant_defense, dispute_type 三列的CSV
输出：清洗后的CSV（去空行、去重、短文本过滤）
"""
import pandas as pd
import re
from pathlib import Path


def clean_dispute_data(input_path: str, output_path: str = None) -> pd.DataFrame:
    """清洗纠纷数据集"""
    # 1. 读取原始数据
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    original_count = len(df)
    print(f"[数据清洗] 原始数据: {original_count} 条")

    # 2. 检查必要列
    required_cols = ['plaintiff_claim', 'defendant_defense']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"缺少必要列: {col}，现有列: {list(df.columns)}")

    # 3. 删除两列都为空的整行
    df = df.dropna(subset=['plaintiff_claim', 'defendant_defense'], how='all')

    # 4. 删除空字符串行
    df = df[df['plaintiff_claim'].astype(str).str.strip() != '']
    df = df[df['defendant_defense'].astype(str).str.strip() != '']

    # 5. 去重
    df = df.drop_duplicates(subset=['plaintiff_claim', 'defendant_defense'])

    # 6. 过滤短文本（少于50字符的认为无效）
    df = df[df['plaintiff_claim'].astype(str).str.len() >= 50]
    df = df[df['defendant_defense'].astype(str).str.len() >= 50]

    # 7. 清理特殊字符
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', str(text))
        return text.strip()

    df['plaintiff_claim'] = df['plaintiff_claim'].apply(clean_text)
    df['defendant_defense'] = df['defendant_defense'].apply(clean_text)
    if 'dispute_type' in df.columns:
        df['dispute_type'] = df['dispute_type'].apply(clean_text)

    df = df.reset_index(drop=True)
    cleaned_count = len(df)
    print(f"[数据清洗] 清洗完成: {cleaned_count} 条 (移除 {original_count - cleaned_count} 条)")

    if output_path:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"[数据清洗] 已保存至: {output_path}")

    return df


if __name__ == '__main__':
    test_path = Path(__file__).parent.parent / 'data' / 'raw_disputes.csv'
    output_path = Path(__file__).parent.parent / 'data' / 'cleaned_disputes.csv'
    if test_path.exists():
        df = clean_dispute_data(str(test_path), str(output_path))
        print(f"清洗后数据样例:")
        print(df[['dispute_type', 'plaintiff_claim']].head(3).to_string(index=False))
    else:
        print(f"数据文件不存在: {test_path}")
        print("请队友A先生成原始数据放到 data/raw_disputes.csv")

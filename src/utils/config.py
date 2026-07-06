"""
项目配置文件
所有可调参数集中管理，方便后期调整
"""
import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# ========== 数据路径 ==========
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw_disputes.csv"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_disputes.csv"
SIMILARITY_CASES_PATH = DATA_DIR / "cleaned_disputes.csv"

# ========== LLM配置（当前使用DeepSeek API） ==========
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "deepseek-chat"),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
    "api_key": os.getenv("LLM_API_KEY", ""),       # ← 你需要填你的key
    "temperature": 0.3,
    "max_retries": 2,
    "timeout": 60,
}

# ========== 工具配置 ==========
TOOL_CONFIG = {
    "sentiment_model": "uer/roberta-base-finetuned-jd-binary-chinese",
    "keyword_top_k": 10,
    "similarity_top_k": 3,
    "similarity_threshold": 0.1,
    "min_text_length": 50,
}

# ========== 界面配置 ==========
GUI_CONFIG = {
    "window_title": "赛博判官 - AI纠纷调解Agent",
    "window_width": 1200,
    "window_height": 800,
}

# ========== 日志 ==========
LOG_CONFIG = {
    "level": "INFO",
    "file": str(ROOT_DIR / "logs" / "app.log"),
}

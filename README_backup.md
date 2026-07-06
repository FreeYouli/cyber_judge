# 赛博判官 - AI纠纷调解Agent

## 项目简介
用户提交争执双方的陈述文本（如室友矛盾、交易纠纷、二手交易争议），Agent通过情感分析、关键词提取、相似案例检索、LLM综合推理，输出结构化判决书（含事实认定、责任划分、和解建议），并生成双方对比雷达图。

## 技术栈
- **语言**：Python 3.10+
- **LLM**：Ollama + Qwen2.5:7b (本地部署)
- **NLP**：Transformers (情感分析)、jieba (关键词)、scikit-learn (TF-IDF检索)
- **界面**：PyQt5
- **可视化**：Matplotlib (雷达图)

## 项目结构

```
cyber_judge/
├── data/                    # 数据文件（CSV）
├── src/
│   ├── data_cleaner.py     # 数据清洗与预处理
│   ├── llm_client.py       # LLM调用封装（Ollama/OpenAI兼容API）
│   ├── tools/
│   │   ├── sentiment_analyzer.py  # 情感分析工具
│   │   ├── keyword_extractor.py   # 关键词提取工具
│   │   └── similarity_search.py   # 相似案例检索工具
│   ├── agent_core.py       # Agent工作流编排
│   ├── utils/
│   │   ├── config.py       # 配置文件（路径/模型/参数）
│   │   └── constants.py    # 常量和模板（判决书Schema/System Prompt）
│   └── gui/
│       ├── main_window.py  # 主界面
│       ├── judgment_panel.py  # 判决书展示面板
│       └── radar_chart.py  # 雷达图
├── tests/                  # 单元测试
├── notebooks/              # 演示用Notebook
├── docs/                   # 文档和报告模板
├── .env.example            # 环境变量模板
└── requirements.txt        # 依赖列表
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动Ollama
```bash
ollama pull qwen2.5:7b
```

### 3. 运行
```bash
python src/main.py
```

## 团队分工
- **架构/Prompt**：项目设计、Prompt工程、模块整合
- **队友A**：数据采集、清洗、标注
- **队友B**：界面开发、报告撰写、PPT
- **Codex**：代码生成

## 开发计划
| 阶段 | 时间 | 产出 |
|------|------|------|
| 基础搭建 | Day 1 | 项目结构 + 数据清洗 + LLM封装 |
| 工具开发 | Day 2-3 | 情感分析/关键词/相似检索 + 端到端命令行 |
| 界面整合 | Day 4-6 | PyQt5界面 + 雷达图 |
| 打磨收尾 | Day 7-14 | 测试/演示案例/报告/PPT |

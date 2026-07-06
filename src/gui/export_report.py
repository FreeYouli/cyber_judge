"""
报告导出模块 - Markdown版本
零依赖，直接写 .md 文件 + 雷达图 PNG
"""
import os
from datetime import datetime

from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DengXian', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import numpy as np

from gui.radar_chart import DIMS


def export_markdown(judgment, plaintiff_text, defendant_text, save_path):
    """
    导出纠纷调解报告（Markdown + 雷达图PNG）

    Args:
        judgment: 判决书字典
        plaintiff_text: 甲方原始陈述
        defendant_text: 乙方原始陈述
        save_path: 保存路径(.md)

    Returns:
        (markdown_path, radar_image_path)
    """
    save_dir = os.path.dirname(save_path)
    base = os.path.splitext(os.path.basename(save_path))[0]

    # 1. 生成雷达图图片
    radar_path = os.path.join(save_dir, f"{base}_radar.png")
    _save_radar(judgment.get("radar_scores", {}), radar_path)

    # 2. 生成 Markdown 内容
    lines = []
    L = lines.append

    L("# ⚖️ 赛博判官 - 纠纷调解报告\n")
    L(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    L("---\n")

    # 一、争议双方陈述
    L("## 一、争议双方陈述\n")
    L("### 👤 甲方陈述\n")
    L(f"> {plaintiff_text}\n")
    L("### 👤 乙方陈述\n")
    L(f"> {defendant_text}\n")
    L("---\n")

    # 二、案件摘要
    L("## 二、案件摘要\n")
    L(f"{judgment.get('case_summary', '无')}\n")

    # 三、情感分析
    L("## 三、情感分析\n")
    sa = judgment.get("party_a_sentiment", {})
    sb = judgment.get("party_b_sentiment", {})
    L(f"- **甲方情绪**：{sa.get('label', '?')}（强度 {sa.get('score', 0):.2f}）\n")
    L(f"- **乙方情绪**：{sb.get('label', '?')}（强度 {sb.get('score', 0):.2f}）\n")
    L("---\n")

    # 四、逻辑漏洞审计
    fallacies = judgment.get("logical_fallacies", [])
    if fallacies:
        L("## 四、逻辑漏洞审计\n")
        for f in fallacies:
            sev = f.get("severity", "轻微")
            sev_icon = {"严重": "🔴", "中等": "🟡", "轻微": "🟢"}.get(sev, "⚪")
            L(f"- {sev_icon} **[{sev}]** {f.get('party', '')}：{f.get('description', '')}\n")
        L("---\n")

    # 五、最终判决
    L("## 五、最终判决\n")
    rs = judgment.get("responsibility_split", {})
    ap = rs.get("party_a", 0)
    bp = rs.get("party_b", 0)
    L(f"### 责任划分\n")
    L(f"- **甲方责任**：{ap}%\n")
    L(f"- **乙方责任**：{bp}%\n")
    if rs.get("description"):
        L(f"- **说明**：{rs['description']}\n")

    sugg = judgment.get("suggestions", "")
    if sugg:
        L(f"### 💡 和解建议\n")
        L(f"{sugg}\n")

    L("---\n")

    # 六、雷达图
    L("## 六、双方表现雷达图\n")
    L(f"![雷达图]({os.path.basename(radar_path)})\n")
    L("\n*本报告由AI生成，仅供参考*\n")

    # 写文件
    with open(save_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return save_path, radar_path


def _save_radar(scores, path):
    """将雷达图保存为PNG（使用静态matplotlib，不依赖Qt）"""
    fig = Figure(figsize=(5, 4), dpi=150)
    ax = fig.add_subplot(111, polar=True)

    n = len(DIMS)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(DIMS, fontsize=11)
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.set_yticklabels([str(i) for i in range(0, 11, 2)], fontsize=8, color="gray")

    for party, color in [("甲方", "#2A6BFF"), ("乙方", "#FF6B6B")]:
        vals = [scores.get(party, {}).get(d, 0) for d in DIMS]
        vals += vals[:1]
        ax.plot(angles, vals, color=color, linewidth=2, label=party)
        ax.fill(angles, vals, color=color, alpha=0.2)

    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1), fontsize=10)
    ax.set_title("双方陈述多维评分对比", pad=18, fontsize=13, fontweight="bold")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    import matplotlib.pyplot as plt
    plt.close(fig)
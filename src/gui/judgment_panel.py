"""
判决书展示面板 - HTML富文本版
v2.0 优化：标题加粗、关键词彩色标签、情感进度条、责任划分大号显示
"""
import sys, os, html as html_mod
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui.radar_chart import RadarChartDialog


# 情感标签 → 颜色映射
SENTIMENT_COLORS = {
    "愤怒": "#FF4444", "委屈": "#FF8C00", "辩解": "#FFAA00",
    "焦虑": "#FF8C00", "失望": "#888888", "中立": "#888888",
    "积极": "#44BB44",
}


class JudgmentPanel(QWidget):
    """判决书展示面板（HTML富文本）"""

    def __init__(self):
        super().__init__()
        self._judgment = None
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 15, 20, 15)

    def show_result(self, j, a_text, b_text):
        self._judgment = j
        self._a_text = a_text
        self._b_text = b_text

        # 清空旧内容
        lo = self.layout()
        while lo.count():
            w = lo.takeAt(0).widget()
            if w: w.deleteLater()

        # 构建HTML
        html = self._build_html(j, a_text, b_text)

        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setText(html)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(False)
        label.setStyleSheet("background:transparent; padding:5px;")
        lo.addWidget(label)

        # 雷达图按钮
        btn = QPushButton("📊 查看雷达图")
        btn.setFixedSize(150, 38)
        btn.setStyleSheet(
            "QPushButton{background:#2A6BFF;color:white;border-radius:8px;"
            "font-size:11pt;font-weight:bold;}"
            "QPushButton:hover{background:#4A8BFF;}"
        )
        btn.clicked.connect(self._open_radar)
        btn_box = QHBoxLayout()
        btn_box.addWidget(btn)
        export_btn = QPushButton("导出报告")
        export_btn.setFixedSize(150, 38)
        export_btn.setStyleSheet("QPushButton{background:#2A6BFF;color:white;border-radius:8px;font-size:11pt;font-weight:bold;}QPushButton:hover{background:#4A8BFF;}")
        export_btn.clicked.connect(self._export_report)
        btn_box.addWidget(export_btn)
        btn_box.addStretch()
        lo.addLayout(btn_box)

    def _build_html(self, j, a_text, b_text):
        h = '<div style="font-family:Microsoft YaHei,sans-serif;font-size:12pt;">'

        # 1. 案件摘要
        h += self._section("📋 案件摘要")
        h += f'<p style="font-size:13pt;color:#D0DCE8;line-height:1.6;margin:8px 0 16px 0;">'
        h += f'{html_mod.escape(j.get("case_summary", ""))}</p>'

        # 2. 证据与关键词分析
        h += self._section("🔍 证据与关键词分析")
        h += '<table width="100%" cellpadding="8"><tr>'

        kw_a = self._get_keywords(a_text)
        kw_b = self._get_keywords(b_text)
        h += self._kw_cell("甲方", "#2A6BFF", kw_a)
        h += self._kw_cell("乙方", "#FF6B6B", kw_b)
        h += '</tr></table>'

        # 3. 情感分析（进度条）
        h += self._section("😊 情感分析")
        sa = j.get("party_a_sentiment", {})
        sb = j.get("party_b_sentiment", {})
        h += self._sentiment_bar("甲方情绪", sa)
        h += self._sentiment_bar("乙方情绪", sb)

        # 4. 逻辑漏洞审计
        fallacies = j.get("logical_fallacies", [])
        if fallacies:
            h += self._section("⚠️ 逻辑漏洞审计")
            for f in fallacies:
                sev = f.get("severity", "轻微")
                sev_color = {"严重": "#FF4444", "中等": "#FF8C00", "轻微": "#44BB44"}
                sev_icon = {"严重": "🔴", "中等": "🟡", "轻微": "🟢"}
                color = sev_color.get(sev, "#888")
                icon = sev_icon.get(sev, "⚪")
                party = html_mod.escape(f.get("party", ""))
                desc = html_mod.escape(f.get("description", ""))
                h += f'<p style="font-size:12pt;color:#D0DCE8;margin:4px 0;">'
                h += f'{icon} <b style="color:{color};">[{sev}]</b> {party}：{desc}'
                h += '</p>'

        # 5. 最终判决与和解建议
        h += self._section("⚖️ 最终判决与和解建议")
        rs = j.get("responsibility_split", {})
        ap = rs.get("party_a", 0)
        bp = rs.get("party_b", 0)

        if ap > bp:
            vcolor = "#FF6B6B"
        elif bp > ap:
            vcolor = "#2A6BFF"
        else:
            vcolor = "#888888"

        h += f'<p style="font-size:20pt;font-weight:bold;color:{vcolor};margin:8px 0;">'
        h += f'责任划分：甲方 {ap}%  /  乙方 {bp}%</p>'

        rs_desc = html_mod.escape(rs.get("description", ""))
        if rs_desc:
            h += f'<p style="font-size:12pt;color:#9ABAD5;margin:4px 0 12px 0;">{rs_desc}</p>'

        sugg = html_mod.escape(j.get("suggestions", ""))
        if sugg:
            h += f'<p style="font-size:13pt;color:#D0DCE8;padding:10px;'
            h += f'background:#243B5A;border-radius:6px;margin:8px 0;">💡 {sugg}</p>'

        # 免责声明
        h += '<hr style="border:none;border-top:1px solid #E0E0E0;margin:16px 0;">'
        h += '<p style="font-size:10pt;color:#7A9AB5;">* 判决由AI生成，仅供参考</p>'

        h += '</div>'
        return h

    def _section(self, title):
        return (f'<h3 style="color:#D4AF37;font-size:14pt;font-weight:bold;'
                f'margin:16px 0 4px 0;">{title}</h3>'
                f'<hr style="border:none;border-top:1px solid #3A5A7A;margin:0 0 8px 0;">')

    def _kw_cell(self, label, color, words):
        h = f'<td width="50%" valign="top">'
        h += f'<p style="font-weight:bold;color:{color};font-size:12pt;margin:0 0 8px 0;">👤 {label}关键词</p>'
        if words:
            tags = ""
            for w in words[:6]:
                tags += (f'<span style="background:{color}22;color:{color};'
                         f'padding:4px 10px;margin:3px;border:1px solid {color}55;'
                         f'font-size:10pt;">{html_mod.escape(w)}</span> ')
            h += f'<p style="line-height:2.2;">{tags}</p>'
        else:
            h += '<p style="color:#999;">无</p>'
        return h + '</td>'

    def _sentiment_bar(self, label, sentiment):
        s = sentiment.get("score", 0)
        label_text = sentiment.get("label", "无")
        color = SENTIMENT_COLORS.get(label_text, "#888888")
        pct = max(5, min(100, int(s * 100)))

        h = f'<p style="font-size:11pt;color:#9ABAD5;margin:6px 0 2px 0;">{label}：{label_text}</p>'
        h += '<table width="100%" cellpadding="0" cellspacing="0" border="0">'
        h += '<tr>'
        h += f'<td width="{pct}%" bgcolor="{color}" height="20" align="center">'
        h += f'<font color="white" size="2">{label_text}</font></td>'
        h += f'<td bgcolor="#243B5A" height="20" align="right">'
        h += f'<font color="#8A9AB5" size="2">{s:.2f}</font></td>'
        h += '</tr></table>'
        return h

    def _get_keywords(self, text):
        if not text:
            return []
        try:
            from tools.keyword_tool import extract_keywords
            return [k["word"] for k in extract_keywords(text, top_k=6)]
        except Exception:
            return text[:20].split("，")[:3] if text else []


    def _export_report(self):
        """导出Markdown报告"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from gui.export_report import export_markdown
        path, _ = QFileDialog.getSaveFileName(
            self.window(), "导出报告", "judgment_report.md",
            "Markdown (*.md);;All (*)")
        if not path: return
        export_markdown(self._judgment, self._a_text, self._b_text, path)
        QMessageBox.information(self.window(), "成功", "报告已保存至: " + path)

    def _open_radar(self):
        if self._judgment:
            dlg = RadarChartDialog(
                self._judgment.get("radar_scores", {}),
                self._judgment.get("case_summary", ""),
                self.window()
            )
            dlg.exec_()
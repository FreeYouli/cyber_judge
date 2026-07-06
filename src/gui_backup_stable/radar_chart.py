# -*- coding: utf-8 -*-
"""雷达图展示窗口 - 800x700独立弹窗（v2.0 修复中文显示）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
# 全局字体配置：优先微软雅黑
matplotlib.rcParams['font.sans-serif'] = [
    'Microsoft YaHei', 'SimHei', 'DengXian',
    'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

DIMS = ["逻辑性", "情感合理性", "证据充分度", "表述清晰度", "说服力"]
COLORS_A = "#2A6BFF"
COLORS_B = "#FF6B6B"


class RadarChartDialog(QDialog):
    """雷达图弹窗"""

    def __init__(self, scores, summary="", parent=None):
        super().__init__(parent)
        self.scores = scores
        self.setWindowTitle("双方陈述表现雷达图")
        self.resize(800, 700)
        self.setStyleSheet("background:#FFFFFF")
        lo = QVBoxLayout(self)
        lo.setContentsMargins(40, 40, 40, 10)

        self.canvas = RadarCanvas(scores, width=6, height=5.5)
        lo.addWidget(self.canvas, alignment=Qt.AlignCenter)

        bot = QHBoxLayout()
        bot.addWidget(QLabel("评分说明：各维度满分10分，基于陈述内容自动计算"))
        bot.addStretch()

        sv = QPushButton("保存图片")
        sv.setFixedSize(110, 36)
        sv.setStyleSheet("QPushButton{background:#2A6BFF;color:white;border-radius:8px;font-weight:bold}")
        sv.clicked.connect(self._save)
        bot.addWidget(sv)

        cl = QPushButton("关闭")
        cl.setFixedSize(80, 36)
        cl.setStyleSheet("QPushButton{background:#E8EDF4;color:#3A4A5A;border-radius:8px}")
        cl.clicked.connect(self.close)
        bot.addWidget(cl)

        lo.addLayout(bot)

    def _save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存雷达图", "radar_chart.png", "PNG (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "成功", f"已保存至：{path}")


class RadarCanvas(FigureCanvas):
    """matplotlib雷达图画布"""

    def __init__(self, scores, width=6, height=5.5, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.scores = scores
        self._plot()

    def _plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111, polar=True)
        n = len(DIMS)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(DIMS, fontsize=12)
        ax.set_ylim(0, 10)
        ax.set_yticks(range(0, 11, 2))
        ax.set_yticklabels([str(i) for i in range(0, 11, 2)], fontsize=8, color="gray")

        for party, color in [("甲方", COLORS_A), ("乙方", COLORS_B)]:
            vals = [self.scores.get(party, {}).get(d, 0) for d in DIMS]
            vals += vals[:1]
            ax.plot(angles, vals, color=color, linewidth=2, label=party)
            ax.fill(angles, vals, color=color, alpha=0.2)

        ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1), fontsize=11)
        ax.set_title("双方陈述多维评分对比", pad=20, fontsize=14, fontweight="bold")

        self.figure.tight_layout()
        self.draw()
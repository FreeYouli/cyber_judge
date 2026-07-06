# -*- coding: utf-8 -*-
"""
雷达图展示窗口 - v3.0
新增：鼠标悬停显示数值 + 维度权重滑块实时更新
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DengXian', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QSlider,
                             QWidget, QCheckBox)
from PyQt5.QtCore import Qt

DIMS = ["逻辑性", "情感合理性", "证据充分度", "表述清晰度", "说服力"]
COLORS_A = "#2A6BFF"
COLORS_B = "#FF6B6B"


class RadarChartDialog(QDialog):
    """雷达图弹窗（支持悬停Tooltip + 权重滑块）"""

    def __init__(self, scores, summary="", parent=None, similar_scores=None):
        super().__init__(parent)
        self.scores = scores
        self.similar_scores = similar_scores
        self._weights = {d: 1.0 for d in DIMS}
        self._compare = False
        self.setWindowTitle("双方陈述表现雷达图")
        self.resize(850, 700)
        self.setStyleSheet("background:#243B5A")
        self._build_ui()

    def _build_ui(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(30, 30, 30, 10)

        # 主体：雷达图 + 右侧滑块
        main = QHBoxLayout()
        self.canvas = RadarCanvas(self.scores, self._weights,
                                  self.similar_scores, self._compare,
                                  width=5.5, height=5.5)
        main.addWidget(self.canvas, stretch=1)
        main.addLayout(self._slider_panel())
        lo.addLayout(main, stretch=1)

        # 底部
        bot = QHBoxLayout()
        self._cb = QCheckBox("对比模式（相似案例）")
        self._cb.setEnabled(self.similar_scores is not None)
        self._cb.toggled.connect(self._toggle_compare)
        bot.addWidget(self._cb)
        bot.addStretch()
        bot.addWidget(QLabel("各维度满分10分"))
        bot.addStretch()
        sv = QPushButton("保存图片"); sv.setFixedSize(110, 36)
        sv.setStyleSheet("QPushButton{background:#2A6BFF;color:white;border-radius:8px;font-weight:bold}")
        sv.clicked.connect(self._save)
        bot.addWidget(sv)
        cl = QPushButton("关闭"); cl.setFixedSize(80, 36)
        cl.setStyleSheet("QPushButton{background:#E8EDF4;color:#3A4A5A;border-radius:8px}")
        cl.clicked.connect(self.close)
        bot.addWidget(cl)
        lo.addLayout(bot)

    def _slider_panel(self):
        """创建维度权重滑块面板"""
        vl = QVBoxLayout()
        vl.setSpacing(8)
        vl.addWidget(QLabel("<b>维度权重</b>"))
        vl.addWidget(QLabel("拖动滑块调整显示权重\n(0.5~1.5，默认1.0)", styleSheet="font-size:9pt;color:#888;"))

        self._sliders = {}
        self._slider_labels = {}
        for dim in DIMS:
            dw = QWidget()
            dl = QVBoxLayout(dw)
            dl.setContentsMargins(0, 0, 0, 0)
            dl.setSpacing(2)

            # 维度名 + 当前值
            h = QHBoxLayout()
            h.addWidget(QLabel(dim, styleSheet="font-size:9pt;"))
            val_lbl = QLabel("1.0")
            val_lbl.setStyleSheet("font-size:9pt;color:#2A6BFF;font-weight:bold;")
            val_lbl.setAlignment(Qt.AlignRight)
            self._slider_labels[dim] = val_lbl
            h.addWidget(val_lbl)
            dl.addLayout(h)

            # 滑块：范围0.5~1.5映射到整数值50~150
            s = QSlider(Qt.Horizontal)
            s.setRange(50, 150)
            s.setValue(100)
            s.setTickPosition(QSlider.TicksBelow)
            s.setTickInterval(10)
            s.valueChanged.connect(lambda v, d=dim: self._on_slider(d, v))
            dl.addWidget(s)
            self._sliders[dim] = s

            vl.addWidget(dw)

        vl.addStretch()
        return vl

    def _on_slider(self, dim, value):
        """滑块值变化，更新权重和雷达图"""
        w = value / 100.0
        self._weights[dim] = round(w, 1)
        self._slider_labels[dim].setText(f"{w:.1f}")
        self.canvas.update_weights(self._weights)

    def _toggle_compare(self, checked):
        self._compare = checked
        self.canvas.update_compare(checked, self.similar_scores)

    def _save(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存雷达图", "radar_chart.png", "PNG (*.png)")
        if path:
            self.canvas.figure.savefig(path, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "成功", f"已保存至：{path}")


class RadarCanvas(FigureCanvas):
    """matplotlib雷达图画布（支持Tooltip和权重）"""

    def __init__(self, scores, weights, similar_scores=None, compare=False,
                 width=5.5, height=5.5, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor="#243B5A")
        super().__init__(self.figure)
        self.scores = scores
        self._weights = weights
        self._similar_scores = similar_scores
        self._compare = compare
        self._vertices = []  # 存储每个顶点的 (角度, 原始分数, 维度名)
        self._tooltip = None
        self._tooltip_visible = False
        self._plot()
        self.mpl_connect('motion_notify_event', self._on_hover)

    def update_weights(self, weights):
        self._weights = weights
        self._plot()
        self.draw_idle()

    def update_compare(self, enabled, similar_scores):
        self._compare = enabled
        self._similar_scores = similar_scores
        self._plot()
        self.draw_idle()

    def _plot(self):
        """绘制雷达图，存储顶点数据用于Tooltip"""
        self.figure.clear()
        ax = self.figure.add_subplot(111, polar=True)
        self.ax = ax

        n = len(DIMS)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(DIMS, fontsize=11, color="#E0E8F0")
        ax.set_ylim(0, 10)
        ax.set_yticks(range(0, 11, 2))
        ax.set_yticklabels([str(i) for i in range(0, 11, 2)], fontsize=8, color="#7A9AB5")

        # 绘制双方
        self._vertices = []
        for party, color, is_main in [("甲方", COLORS_A, True), ("乙方", COLORS_B, True)]:
            raw_scores = self.scores.get(party, {})
            vals = []
            for d in DIMS:
                base = raw_scores.get(d, 0)
                w = self._weights.get(d, 1.0)
                vals.append(min(10, base * w))
            vals += vals[:1]

            line = ax.plot(angles, vals, color=color, linewidth=2, label=party)[0]
            ax.fill(angles, vals, color=color, alpha=0.2)

            # 存储顶点 (angle, weighted_score, dim_name)
            for i in range(n):
                self._vertices.append({
                    "angle": angles[i],
                    "score": round(vals[i], 1),
                    "dim": DIMS[i],
                    "party": party,
                    "color": color,
                })

        # 相似案例（对比模式）
        if self._compare and self._similar_scores:
            sim = self._similar_scores.get("甲方", {})
            vals = [sim.get(d, 0) for d in DIMS] + [sim.get(DIMS[0], 0)]
            ax.plot(angles, vals, color="#888888", linewidth=2, linestyle="--",
                    label="相似案例", alpha=0.7)

        ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1), fontsize=10)
        ax.set_title("双方陈述多维评分对比", pad=18, fontsize=13, fontweight="bold", color="#D4AF37")

        # Tooltip annotation（不显示，鼠标悬停时才显示）
        self._tooltip = ax.annotate(
            "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#888", alpha=0.9),
            fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#888", lw=0.8),
            zorder=100
        )
        self._tooltip.set_visible(False)
        self._tooltip_visible = False

        self.figure.tight_layout()

    def _on_hover(self, event):
        """鼠标悬停检测，显示Tooltip"""
        if event.inaxes != self.ax:
            if self._tooltip_visible:
                self._tooltip.set_visible(False)
                self._tooltip_visible = False
                self.draw_idle()
            return

        # 检测鼠标是否靠近某个顶点
        threshold = 0.4  # 极坐标下的距离阈值
        closest = None
        min_dist = threshold

        for v in self._vertices:
            dx = event.xdata - v["angle"] if event.xdata is not None else 999
            dy = event.ydata - v["score"] if event.ydata is not None else 999
            dist = np.sqrt(dx**2 + dy**2)
            if dist < min_dist:
                min_dist = dist
                closest = v

        if closest:
            self._tooltip.xy = (closest["angle"], closest["score"])
            self._tooltip.set_text(f"{closest['party']} - {closest['dim']}: {closest['score']}分")
            self._tooltip.set_color(closest["color"])
            self._tooltip.set_visible(True)
            self._tooltip_visible = True
            self.draw_idle()
        else:
            if self._tooltip_visible:
                self._tooltip.set_visible(False)
                self._tooltip_visible = False
                self.draw_idle()
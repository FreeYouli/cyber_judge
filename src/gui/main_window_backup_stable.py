# -*- coding: utf-8 -*-
"""赛博判官主界面 - v1.1（修复线程回收 + 禁用样式）"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from agent_core import CyberJudge
from gui.radar_chart import RadarChartDialog


class JudgeWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    def __init__(self, a, b):
        super().__init__(); self.a = a; self.b = b
    def run(self):
        try:
            print("[Worker] 开始分析...")
            j = CyberJudge(); r = j.judge(self.a, self.b, verbose=False)
            print("[Worker] 分析完成")
            self.finished.emit(r)
        except Exception as e:
            print("[Worker] 错误:", e)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("赛博判官 -- AI纠纷调解员")
        self.resize(1100, 800); self.setMinimumSize(900, 650)
        self.setStyleSheet("background:#F0F4FA")
        self._panel = None
        self._worker = None  # 保持线程引用，防止GC回收
        self._build()

    def _build(self):
        c = QWidget(); self.setCentralWidget(c); r = QVBoxLayout(c)
        r.setContentsMargins(20,10,20,10); r.setSpacing(10)
        r.addWidget(self._title())
        r.addLayout(self._inputs())
        r.addWidget(self._btns(), alignment=Qt.AlignCenter)
        self._init_bar()
        r.addWidget(self._bar)
        self._sc = QScrollArea(); self._sc.setWidgetResizable(True)
        self._sc.setStyleSheet("QScrollArea{background:#FFF;border-radius:12px;border:none}")
        r.addWidget(self._sc, stretch=1)
        r.addWidget(self._statusbar())
        self._placeholder()

    def _title(self):
        w = QWidget(); lo = QHBoxLayout(w); lo.setContentsMargins(0,0,0,0)
        t = QLabel("赛博判官")
        t.setStyleSheet("font-size:24pt;font-weight:bold;color:#1A2A4A")
        lo.addWidget(t); lo.addStretch()
        v = QLabel("AI纠纷调解员 v1.0")
        v.setStyleSheet("font-size:10pt;color:#7A8A9A")
        lo.addWidget(v); return w

    def _inputs(self):
        lo = QHBoxLayout(); lo.setSpacing(20)
        self._ta = self._edit("甲方纠纷陈述...")
        self._tb = self._edit("乙方纠纷陈述...")
        lo.addWidget(self._wrap("甲方陈述", self._ta))
        lo.addWidget(self._wrap("乙方陈述", self._tb))
        return lo

    def _edit(self, p):
        e = QTextEdit(); e.setPlaceholderText(p)
        e.setFixedSize(500, 220)
        e.setStyleSheet("""
            QTextEdit{border:2px solid #B0C4DE;
                border-radius:8px;padding:8px;
                font-size:11pt;color:#2A3A4A;background:white;}
            QTextEdit:focus{border-color:#2A6BFF;}
        """)
        return e

    def _wrap(self, l, e):
        w = QWidget(); lo = QVBoxLayout(w); lo.setContentsMargins(0,0,0,0)
        lbl = QLabel(l); lbl.setStyleSheet("font-size:12pt;color:#1A2A4A;font-weight:bold")
        lo.addWidget(lbl); lo.addWidget(e); return w

    def _btns(self):
        w = QWidget(); lo = QHBoxLayout(w)
        lo.setAlignment(Qt.AlignCenter); lo.setSpacing(40)
        self._jb = QPushButton("开始裁决")
        self._jb.setFixedSize(140, 48)
        self._jb.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #2A6BFF,stop:1 #1A4FD0);color:white;
                border-radius:10px;font-size:14pt;font-weight:bold;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #4A8BFF,stop:1 #2A6BFF);}
            QPushButton:disabled{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #6A8BFF,stop:1 #4A6BFF);color:rgba(255,255,255,200);}
        """)
        self._jb.clicked.connect(self._judge)
        lo.addWidget(self._jb)
        cb = QPushButton("清空内容")
        cb.setFixedSize(120, 48)
        cb.setStyleSheet("""
            QPushButton{background:#E8EDF4;color:#3A4A5A;
                border-radius:10px;font-size:12pt;}
            QPushButton:hover{background:#F5E6E6;color:#D04040;}
        """)
        cb.clicked.connect(self._clear)
        lo.addWidget(cb); return w

    def _init_bar(self):
        self._bar = QProgressBar(); self._bar.setRange(0,0); self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet("""
            QProgressBar{background:#D0D8E4;border:none;border-radius:2px;}
            QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #2A6BFF,stop:1 #4A8BFF);border-radius:2px;}
        """)
        self._bar.hide()

    def _statusbar(self):
        w = QWidget(); lo = QHBoxLayout(w); lo.setContentsMargins(0,4,0,0)
        self._st = QLabel("就绪")
        self._st.setStyleSheet("font-size:10pt;color:#7A8A9A")
        lo.addWidget(self._st); lo.addStretch()
        lo.addWidget(QLabel("已加载149条案例"))
        return w

    def _placeholder(self):
        w = QWidget(); lo = QVBoxLayout(w); lo.setAlignment(Qt.AlignCenter)
        lo.addWidget(QLabel("输入双方陈述，点击裁决开始审判"))
        self._sc.setWidget(w)

    def _judge(self):
        a = self._ta.toPlainText().strip()
        b = self._tb.toPlainText().strip()
        if not a or not b: self._st.setText("请先输入双方陈述"); return
        if len(a) < 20 or len(b) < 20: self._st.setText("陈述内容过短"); return
        self._jb.setEnabled(False)
        self._jb.setText("分析中...")
        self._bar.show()
        self._st.setText("正在分析双方陈述...")
        self._worker = JudgeWorker(a, b)
        self._worker.finished.connect(self._done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _done(self, r):
        self._jb.setEnabled(True)
        self._jb.setText("开始裁决")
        self._bar.hide()
        self._st.setText("裁决完成")
        from gui.judgment_panel import JudgmentPanel
        if not self._panel: self._panel = JudgmentPanel()
        self._sc.setWidget(self._panel)
        self._panel.show_result(r, self._ta.toPlainText(), self._tb.toPlainText())
        self._worker = None

    def _on_error(self, msg):
        self._jb.setEnabled(True)
        self._jb.setText("开始裁决")
        self._bar.hide()
        self._st.setText("出错了")
        QMessageBox.critical(self, "裁决失败", msg)
        self._worker = None

    def _clear(self):
        self._ta.clear(); self._tb.clear()
        self._placeholder(); self._st.setText("就绪")


def main():
    app = QApplication(sys.argv); app.setStyle("Fusion")
    MainWindow().show(); sys.exit(app.exec_())

if __name__ == "__main__":
    main()
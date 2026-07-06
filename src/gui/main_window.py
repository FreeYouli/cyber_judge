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
        self.setWindowTitle("赛博判官⚖️ -- AI纠纷调解员")
        self.resize(1100, 800); self.setMinimumSize(900, 650)
        self.setStyleSheet("background:#1A2A4A")
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
        self._sc.setObjectName("resultArea")
        r.addWidget(self._sc, stretch=1)
        r.addWidget(self._statusbar())
        self._placeholder()
        self._current_theme = "dark_gold"
        self._add_theme_combo()
        self._apply_theme()
        self._current_theme = "dark_gold"
        self._apply_theme()

    def _add_theme_combo(self):
        """在标题栏添加风格切换下拉菜单"""
        from PyQt5.QtWidgets import QToolButton, QMenu, QAction
        self._theme_menu = QMenu()
        self._theme_menu.setObjectName("themeMenu")
        for text, key in [("🌙 暗夜霓虹","neon"),("✨ 极简白金","platinum"),("🚀 深蓝金科技","dark_gold"),("🏛️ 墨绿金复古","green_gold")]:
            action = QAction(text, self._theme_menu)
            action.triggered.connect(lambda checked, k=key: self._switch_theme(k))
            self._theme_menu.addAction(action)
        self._theme_btn = QToolButton()
        self._theme_btn.setObjectName("themeBtn")
        self._theme_btn.setText("🚀 深蓝金科技")
        self._theme_btn.setPopupMode(QToolButton.InstantPopup)
        self._theme_btn.setMenu(self._theme_menu)
        bar = self.findChildren(QWidget)[0]
        if bar:
            lo = bar.layout()
            lo.insertWidget(lo.count() - 1, self._theme_btn)

    def _apply_theme(self):
        """用当前主题调色板重新绘制所有控件"""
        print(f"[Theme] Applying: {self._current_theme}")
        from gui.styles import get as get_theme
        p = get_theme(self._current_theme)
        print(f"[Theme] gold={p.get(chr(103)+chr(111)+chr(108)+chr(100),chr(63))}, input_bg={p.get(chr(105)+chr(110)+chr(112)+chr(117)+chr(116)+chr(95)+chr(98)+chr(103),chr(63))}")
        self.setStyleSheet("QMainWindow{background:" + p["bg"] + ";}")
        tl = self.findChild(QLabel, "titleLabel")
        if tl: tl.setStyleSheet("font-size:24pt;font-weight:bold;color:" + p["txt"]["title"] + ";background:transparent;")
        vl = self.findChild(QLabel, "versionLabel")
        if vl: vl.setStyleSheet("font-size:10pt;color:" + p["txt"]["subtitle"] + ";background:transparent;")
        il = self.findChild(QLabel, "inputLabel")
        if il: il.setStyleSheet("font-size:12pt;color:" + p["gold"] + ";font-weight:bold;background:transparent;")
        for ie in self.findChildren(QTextEdit): ie.setStyleSheet("QTextEdit{background:" + p["input_bg"] + ";color:" + p["txt"]["input"] + ";border:2px solid " + p["border"] + ";border-radius:8px;padding:8px;font-size:11pt;}QTextEdit:focus{border-color:" + p["focus"] + ";}QTextEdit::placeholder{color:" + p["txt"]["placeholder"] + ";}")
        jb = self.findChild(QPushButton, "judgeBtn")
        if jb: jb.setStyleSheet("QPushButton{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 " + p["gold"] + ",stop:1 " + p["gold2"] + ");color:" + p["btn_text"] + ";border-radius:10px;font-size:14pt;font-weight:bold;}QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 " + p["focus"] + ",stop:1 " + p["gold"] + ");}QPushButton:disabled{background:" + p["muted"] + ";color:rgba(255,255,255,100);}")
        cb = self.findChild(QPushButton, "clearBtn")
        if cb: cb.setStyleSheet("QPushButton{background:transparent;color:" + p["gold"] + ";border-radius:10px;font-size:12pt;border:1px solid " + p["gold"] + ";}QPushButton:hover{background:rgba(0,0,0,0.05);color:" + p["focus"] + ";}")
        pb = self.findChild(QProgressBar, "progressBar")
        if pb: pb.setStyleSheet("QProgressBar{background:" + p["border"] + ";border:none;border-radius:2px;}QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 " + p["gold"] + ",stop:1 " + p["gold2"] + ");border-radius:2px;}")
        sa = self.findChild(QScrollArea, "resultArea")
        if sa: sa.setStyleSheet("QScrollArea{background:" + p["card"] + ";border-radius:12px;border:1px solid " + p["border"] + ";}")
        if sa.viewport(): sa.viewport().setStyleSheet("background:" + p["card"] + ";")
        if sa.widget(): sa.widget().setStyleSheet("background:" + p["card"] + ";")
        st = self.findChild(QLabel, "statusLabel")
        if st: st.setStyleSheet("font-size:10pt;color:" + p["txt"]["status"] + ";background:transparent;")
        ph = self.findChild(QLabel, "placeholderLabel")
        if ph: ph.setStyleSheet("font-size:14pt;color:" + p["txt"]["body"] + ";background:transparent;")
        tb = self.findChild(QToolButton, "themeBtn")
        if tb: tb.setStyleSheet("QToolButton{background:transparent;color:" + p["gold"] + ";border:none;font-size:10pt;padding:2px 4px;}QToolButton::menu-indicator{image:none;}")
        if hasattr(self, '_theme_menu') and self._theme_menu: self._theme_menu.setStyleSheet("QMenu{background:" + p["card"] + ";color:" + p["text"] + ";border:1px solid " + p["border"] + ";}QMenu::item{padding:6px 20px;font-size:10pt;}QMenu::item:selected{background:" + p["gold"] + ";color:" + p["btn_text"] + ";}")

    def _switch_theme(self, name):
        """切换配色主题"""
        from gui.styles import PALETTES
        if name in PALETTES:
            self._current_theme = name
            self._apply_theme()
            if hasattr(self, '_theme_btn'):
                emoji_map = {"neon":"🌙","platinum":"✨","dark_gold":"🚀","green_gold":"🏛️"}
                self._theme_btn.setText(emoji_map.get(name,"") + " " + PALETTES[name]["name"])

    def _title(self):
        w = QWidget(); lo = QHBoxLayout(w); lo.setContentsMargins(0,0,0,0)
        t = QLabel("赛博判官")
        t.setStyleSheet("font-size:24pt;font-weight:bold;color:#D4AF37")
        lo.addWidget(t); lo.addStretch()
        v = QLabel("AI纠纷调解员 v1.0")
        v.setStyleSheet("font-size:10pt;color:rgba(201,168,76,0.6)")
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
        e.setObjectName("inputEdit")
        return e

    def _wrap(self, l, e):
        w = QWidget(); lo = QVBoxLayout(w); lo.setContentsMargins(0,0,0,0)
        lbl = QLabel(l); lbl.setObjectName("inputLabel")
        lo.addWidget(lbl); lo.addWidget(e); return w

    def _btns(self):
        w = QWidget(); lo = QHBoxLayout(w)
        lo.setAlignment(Qt.AlignCenter); lo.setSpacing(40)
        self._jb = QPushButton("开始裁决")
        self._jb.setObjectName("judgeBtn")
        self._jb.setFixedSize(140, 48)
        self._jb.setStyleSheet("""
            QPushButton{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #D4AF37,stop:1 #A8893A);color:#FFFFFF;
                border-radius:10px;font-size:14pt;font-weight:bold;}
            QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #DDBE5C,stop:1 #D4AF37);}
            QPushButton:disabled{background:#3A4A5A;color:rgba(255,255,255,100);}
        """)
        self._jb.clicked.connect(self._judge)
        lo.addWidget(self._jb)
        cb = QPushButton("清空内容")
        cb.setObjectName("clearBtn")
        cb.setFixedSize(120, 48)

        cb.clicked.connect(self._clear)
        lo.addWidget(cb); return w

    def _init_bar(self):
        self._bar = QProgressBar(); self._bar.setRange(0,0); self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet("""
            QProgressBar{background:#2A4060;border:none;border-radius:2px;}
            QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #D4AF37,stop:1 #DDBE5C);border-radius:2px;}
        """)
        self._bar.hide()

    def _statusbar(self):
        w = QWidget(); lo = QHBoxLayout(w); lo.setContentsMargins(0,4,0,0)
        self._st = QLabel("就绪")
        self._st.setStyleSheet("font-size:10pt;color:rgba(201,168,76,0.6)")
        lo.addWidget(self._st); lo.addStretch()
        lo.addWidget(QLabel("已加载149条案例"))
        return w

    def _placeholder(self):
        w = QWidget(); lo = QVBoxLayout(w); lo.setAlignment(Qt.AlignCenter)
        t = QLabel("输入双方陈述，点击裁决开始审判"); t.setObjectName("placeholderLabel"); lo.addWidget(t)
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
        self._placeholder()
        self._panel = None
        self._apply_theme()
        self._st.setText("就绪")


def main():
    app = QApplication(sys.argv); app.setStyle("Fusion")
    MainWindow().show(); sys.exit(app.exec_())

if __name__ == "__main__":
    main()
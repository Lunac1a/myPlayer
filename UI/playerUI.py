import platform
from tool.detect import detect_running_music_app
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QPushButton
)
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QTimer
import requests
from threading import Thread

music_app = detect_running_music_app()

if platform.system() == "Windows":
    if music_app == "qq":
        from infoFetch.Windows.qqMusic.fetcher import get_current_track
    elif music_app == "netease":
        from infoFetch.Windows.netease.fetcher import get_current_track
elif platform.system() == "Darwin":
    from infoFetch.macOS.fetcher import get_current_track

class MusicPlayerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Player")
        self.setGeometry(300, 300, 400, 210)

        # 去掉边框和标题栏
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        # ------------------ 封面 ------------------
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(150, 150)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet("border-radius:10px;")

        # ------------------ 信息块 ------------------
        self.info_widget = QWidget()
        self.info_widget.setFixedHeight(self.cover_label.height())
        self.info_widget.setStyleSheet("""
            background-color: rgba(50, 50, 50, 220);
            border-radius: 10px;
        """)

        self.title_label = QLabel("歌曲名")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background: transparent;")
        self.title_label.setWordWrap(True)
        self.artist_label = QLabel("歌手")
        self.artist_label.setStyleSheet("font-size: 14px; color: white; background: transparent;")
        self.artist_label.setWordWrap(True)

        info_layout = QVBoxLayout()
        info_layout.addStretch()
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addStretch()
        info_layout.setContentsMargins(15, 10, 15, 10)
        self.info_widget.setLayout(info_layout)

        #------------------ 退出按钮 ------------------
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 50, 50, 180);
                color: white;
                border: none;
                font-size: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 80, 80, 220);
            }
        """)
        self.close_button.setFixedSize(20, 20)
        self.close_button.move(10, 10)  # 左上角
        self.close_button.hide()  # 默认隐藏
        self.close_button.raise_()   # 始终在最上层
        self.close_button.clicked.connect(self.close)

        # ------------------ 主布局 ------------------
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.cover_label)
        main_layout.addWidget(self.info_widget)
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 15px;")

        # ------------------ 状态 ------------------
        self.last_songmid = None

        # 定时器刷新 UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

        # 拖动窗口变量
        self._drag_pos = None

    def update_ui(self):
        track = get_current_track()
        if not track:
            return

        # 切歌才更新
        if track['songmid'] != self.last_songmid:
            self.last_songmid = track['songmid']
            self.title_label.setText(track['title'])
            self.artist_label.setText(track['author'])

            cover_url = track.get('cover')
            if cover_url:  # 有封面才异步加载
                self.load_cover_async(cover_url)
            else:  # 没封面就清空或设置默认
                self.cover_label.clear()  # 清空

    def load_cover_async(self, url):
        """异步下载封面并高质量缩放"""
        def download():
            try:
                resp = requests.get(url, timeout=5)
                pixmap = QPixmap()
                pixmap.loadFromData(resp.content)
                dpi_ratio = 2.0
                scaled = pixmap.scaled(
                    int(self.cover_label.width() * dpi_ratio),
                    int(self.cover_label.height() * dpi_ratio),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                scaled.setDevicePixelRatio(dpi_ratio)
                self.cover_label.setPixmap(scaled)
            except:
                pass
        Thread(target=download, daemon=True).start()

    # -----------------------------
    # 拖动窗口功能
    # -----------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    # 鼠标进入事件
    def enterEvent(self, event):
        self.close_button.show()
        super().enterEvent(event)

    # 鼠标离开事件
    def leaveEvent(self, event):
        self.close_button.hide()
        super().leaveEvent(event)

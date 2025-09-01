import sys
import platform
from threading import Thread
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import requests

if platform.system() == "Windows":
    from infoFetch.Windows.fetcher import get_current_track
elif platform.system() == "Darwin":  # macOS
    from infoFetch.macOS.fetcher import get_current_track

class MusicPlayerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Player")
        self.setGeometry(300, 300, 400, 200)

        # 封面
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(150, 150)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 歌曲名
        self.title_label = QLabel("歌曲名")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # 歌手
        self.artist_label = QLabel("歌手")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setStyleSheet("font-size: 14px;")

        # 布局
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.cover_label)
        main_layout.addLayout(info_layout)

        self.setLayout(main_layout)

        # 内部状态
        self.last_songmid = None
        self.current_time = 0
        self.track_duration = 1

        # 定时器刷新 UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

    def update_ui(self):
        track = get_current_track()
        if not track:
            return

        # 只有歌曲切换才更新文字和封面
        if track['songmid'] != self.last_songmid:
            self.last_songmid = track['songmid']
            self.title_label.setText(track['title'])
            self.artist_label.setText(track['author'])
            self.track_duration = track.get('duration', 1)
            self.current_time = 0
            self.load_cover_async(track['cover'])

    def load_cover_async(self, url):
        """异步下载封面并高质量缩放"""
        def download():
            try:
                resp = requests.get(url, timeout=5)
                pixmap = QPixmap()
                pixmap.loadFromData(resp.content)

                # 高 DPI 缩放处理
                dpi_ratio = 2.0
                scaled_pixmap = pixmap.scaled(
                    int(self.cover_label.width() * dpi_ratio),
                    int(self.cover_label.height() * dpi_ratio),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # 设置设备像素比
                scaled_pixmap.setDevicePixelRatio(dpi_ratio)

                # 更新 QLabel
                self.cover_label.setPixmap(scaled_pixmap)
                self.cover_label.setScaledContents(False)
                self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            except Exception as e:
                print("封面加载失败:", e)

        Thread(target=download, daemon=True).start()



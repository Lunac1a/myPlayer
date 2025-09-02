import platform
import sys
from PyQt6.QtWidgets import QApplication
from UI.playerUI import MusicPlayerUI
from tool.detect import detect_running_music_app

music_app = detect_running_music_app()

# 根据系统选择 fetcher
if platform.system() == "Windows":
    if music_app == "qq":
        from infoFetch.Windows.qqMusic.fetcher import start_fetcher
    elif music_app == "netease":
        from infoFetch.Windows.netease.fetcher import start_fetcher
elif platform.system() == "Darwin":
    if music_app == "qq":
        from infoFetch.macOS.fetcher import start_fetcher

if __name__ == "__main__":
    # 启动 fetcher 后台线程
    start_fetcher()

    app = QApplication(sys.argv)
    player_ui = MusicPlayerUI()
    player_ui.show()
    sys.exit(app.exec())

import platform
import sys

from PyQt6.QtWidgets import QApplication

from UI.playerUI import MusicPlayerUI

if platform.system() == "Windows":
    from infoFetch.Windows.fetcher import start_fetcher
elif platform.system() == "Darwin":  # macOS
    from infoFetch.macOS.fetcher import start_fetcher

if __name__ == "__main__":
    # 启动 fetcher 后台线程
    start_fetcher()

    app = QApplication(sys.argv)
    player_ui = MusicPlayerUI()
    player_ui.show()
    sys.exit(app.exec())
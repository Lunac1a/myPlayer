import platform
import sys
from PyQt6.QtWidgets import QApplication
from UI.playerUI import MusicPlayerUI


# 根据系统选择 fetcher
if platform.system() == "Windows":
    from infoFetch.Windows.fetcher import start_fetcher
elif platform.system() == "Darwin":  # macOS
    from infoFetch.macOS.fetcher import start_fetcher

if __name__ == "__main__":
    # 启动 fetcher 后台线程
    # 注意：这里传入获取当前歌曲信息的函数
    start_fetcher()

    app = QApplication(sys.argv)
    player_ui = MusicPlayerUI()
    player_ui.show()
    sys.exit(app.exec())

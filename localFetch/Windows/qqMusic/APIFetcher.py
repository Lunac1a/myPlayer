import psutil
import win32gui
import win32process

def parse_window_title(title: str):
    """解析 QQMusic 窗口标题 '歌曲名 - 歌手'"""
    if " - " in title:
        title_part, artist_part = title.split(" - ", 1)
        return title_part.strip(), artist_part.strip()
    return title.strip(), ""

def get_now_playing_title():
    """返回第一个 QQMusic 窗口的歌曲名和歌手"""
    for proc in psutil.process_iter(['pid', 'name']):
        if "QQMusic" in proc.info['name']:
            pid = proc.info['pid']
            titles = []

            def callback(hwnd, _):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        titles.append(title)
                return True

            win32gui.EnumWindows(callback, None)
            if titles:
                return parse_window_title(titles[0])
    return None, None

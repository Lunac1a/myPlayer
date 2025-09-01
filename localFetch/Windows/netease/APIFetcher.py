import psutil
import win32gui
import win32process

def parse_window_title(title: str):
    """解析网易云音乐窗口标题 '歌曲名 - 歌手'"""
    if " - " in title:
        return title.split(" - ", 1)
    return title, ""

def get_now_playing_title():
    """返回第一个网易云音乐窗口的歌曲名和歌手"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'cloudmusic' in proc.info['name'].lower():
            pid = proc.info['pid']
            titles = []

            def callback(hwnd, _):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    if text:
                        titles.append(text)
                return True

            win32gui.EnumWindows(callback, None)
            if titles:
                return parse_window_title(titles[0])
    return None, None

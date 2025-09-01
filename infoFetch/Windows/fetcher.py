import psutil
import win32gui
import win32process
import hashlib

from threading import Thread, Lock
import time

from request.qqMusic import get_track_info

_current_track = None
_lock = Lock()

def get_current_track():
    with _lock:
        return _current_track.copy() if _current_track else None

def set_current_track(track):
    global _current_track
    with _lock:
        _current_track = track

def _parse_window_title(title: str):
    """解析 QQMusic 窗口标题 '歌曲名 - 歌手'"""
    if " - " in title:
        title_part, artist_part = title.split(" - ", 1)
        return title_part.strip(), artist_part.strip()
    return title.strip(), ""

def _get_qqmusic_window_title():
    """返回第一个 QQMusic 窗口的标题"""
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
                return titles[0]
    return None

def _fetch_loop(poll_interval=0.5):
    last_hash = None
    while True:
        title = _get_qqmusic_window_title()
        if title:
            song_title, artist = _parse_window_title(title)
            song_hash = hashlib.md5(f"{song_title}-{artist}".encode('utf-8')).hexdigest()

            if song_hash != last_hash:
                last_hash = song_hash
                # 调用 qqMusic 搜索接口获取封面和时长
                track_info = get_track_info(f"{song_title} - {artist}")
                if track_info:
                    set_current_track(track_info)
                else:
                    # 没搜到就先填基本信息
                    set_current_track({
                        "songmid": song_hash,
                        "title": song_title,
                        "author": artist,
                        "cover": "",
                        "duration": 0
                    })
        time.sleep(poll_interval)

def start_fetcher():
    Thread(target=_fetch_loop, daemon=True).start()

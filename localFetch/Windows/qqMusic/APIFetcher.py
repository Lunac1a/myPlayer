import time
import ctypes
from ctypes import wintypes
from threading import Thread, Lock

POLL_INTERVAL = 1  # 每秒查询一次
_current_track = None
_lock = Lock()

# --- Windows API --- #
user32 = ctypes.WinDLL('user32', use_last_error=True)
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextW = user32.GetWindowTextW
IsWindowVisible = user32.IsWindowVisible
GetWindowThreadProcessId = user32.GetWindowThreadProcessId
OpenProcess = ctypes.windll.kernel32.OpenProcess
QueryFullProcessImageName = ctypes.windll.kernel32.QueryFullProcessImageNameW
CloseHandle = ctypes.windll.kernel32.CloseHandle

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

def get_qqmusic_window_title():
    """遍历所有窗口，找到 QQMusic 的窗口标题"""
    titles = []

    def enum_proc(hwnd, lParam):
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buffer, length + 1)

        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h_process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        exe_name = ""
        if h_process:
            exe_name_buffer = ctypes.create_unicode_buffer(512)
            size = ctypes.wintypes.DWORD(512)
            if QueryFullProcessImageName(h_process, 0, exe_name_buffer, ctypes.byref(size)):
                exe_name = exe_name_buffer.value.split("\\")[-1]
            CloseHandle(h_process)

        if exe_name.lower() == "qqmusic.exe":
            titles.append(buffer.value)
        return True

    EnumWindows(EnumWindowsProc(enum_proc), 0)

    # 返回第一个符合歌曲格式的
    for t in titles:
        if " - " in t:
            return t
    return None

def _fetch_loop():
    global _current_track
    last_title = None

    while True:
        try:
            now_playing_text = get_qqmusic_window_title()
            if now_playing_text and now_playing_text != last_title:
                last_title = now_playing_text
                with _lock:
                    _current_track = now_playing_text
                print("Now Playing updated:", now_playing_text)  # 调试输出
        except Exception as e:
            print("发生错误:", e)

        time.sleep(POLL_INTERVAL)

def start_fetcher():
    thread = Thread(target=_fetch_loop, daemon=True)
    thread.start()
    return thread

def get_current_track():
    with _lock:
        return _current_track

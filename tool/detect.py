import psutil

def detect_running_music_app():
    """返回当前运行的音乐软件名称"""
    for proc in psutil.process_iter(['name']):
        name = proc.info['name'].lower()
        if "qqmusic" in name:
            return "qq"
        elif "cloudmusic" in name or "netease" in name:
            return "netease"
    return None

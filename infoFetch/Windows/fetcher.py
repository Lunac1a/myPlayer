import time
from threading import Thread, Lock
from request.qqMusic import get_track_info
from localFetch.Windows.qqMusic.APIFetcher import get_qqmusic_window_title

POLL_INTERVAL = 1  # 每秒轮询一次
_current_track = None
_lock = Lock()

def _fetch_loop():
    global _current_track
    last_songmid = None

    while True:
        try:
            now_playing_text = get_qqmusic_window_title()
            if now_playing_text and " - " in now_playing_text:
                track = get_track_info(now_playing_text)
                if track:
                    if track['songmid'] != last_songmid:
                        last_songmid = track['songmid']
                        with _lock:
                            _current_track = track
                        print("Now Playing: ", track['title'], "-", track['author'])
        except Exception as e:
            print("发生错误:", e)

        time.sleep(POLL_INTERVAL)

def start_fetcher():
    thread = Thread(target=_fetch_loop, daemon=True)
    thread.start()
    return thread

def get_current_track():
    with _lock:
        return _current_track.copy() if _current_track else None

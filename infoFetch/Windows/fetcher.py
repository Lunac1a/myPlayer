import time
import hashlib
from threading import Thread, Lock
from request.qqMusic import get_track_info
from localFetch.Windows.qqMusic.APIFetcher import get_now_playing_title

_current_track = None
_lock = Lock()

def get_current_track():
    with _lock:
        return _current_track.copy() if _current_track else None

def set_current_track(track):
    global _current_track
    with _lock:
        _current_track = track

def _fetch_loop(poll_interval=0.5):
    last_hash = None
    while True:
        title, artist = get_now_playing_title()
        if title:
            song_hash = hashlib.md5(f"{title}-{artist}".encode('utf-8')).hexdigest()
            if song_hash != last_hash:
                last_hash = song_hash
                # 调用 qqMusic 获取封面和时长
                track_info = get_track_info(f"{title} - {artist}")
                if track_info:
                    set_current_track(track_info)
                else:
                    set_current_track({
                        "songmid": song_hash,
                        "title": title,
                        "author": artist,
                        "cover": "",
                        "duration": 0
                    })
        time.sleep(poll_interval)

def start_fetcher():
    Thread(target=_fetch_loop, daemon=True).start()

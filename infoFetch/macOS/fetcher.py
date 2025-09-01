import time
from threading import Thread, Lock
from request.qqMusic import get_track_info
from localFetch.macOS.AppleScriptFetcher import get_qqmusic_now_playing

POLL_INTERVAL = 1  # 每秒查询一次
_current_track = None
_lock = Lock()

def _fetch_loop():
    global _current_track
    last_songmid = None

    while True:
        try:
            now_playing_text = get_qqmusic_now_playing()
            if now_playing_text and " - " in now_playing_text:
                track = get_track_info(now_playing_text)
                if track:
                    if track['songmid'] != last_songmid:
                        last_songmid = track['songmid']
                        with _lock:
                            _current_track = track
                        print("更新当前播放:", track['title'], "-", track['author'])
        except Exception as e:
            print("发生错误:", e)

        time.sleep(POLL_INTERVAL)

def start_fetcher():
    """
    启动后台线程轮询 APF + QQ音乐接口
    """
    thread = Thread(target=_fetch_loop, daemon=True)
    thread.start()
    return thread

def get_current_track():
    """
    返回当前播放歌曲 JSON 对象
    """
    with _lock:
        return _current_track.copy() if _current_track else None

# 示例运行
if __name__ == "__main__":
    start_fetcher()
    last_songmid = None

    try:
        while True:
            track = get_current_track()
            if track:
                # 只有 songmid 不一样时才更新
                if track['songmid'] != last_songmid:
                    last_songmid = track['songmid']
                    print(track['title'], track['author'], track['cover'])
            time.sleep(1)  # 每秒轮询一次
    except KeyboardInterrupt:
        print("已停止")
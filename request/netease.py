import re
import requests

def parse_now_playing(text):
    """
    解析输出，返回 title 和 artist
    输入示例: "孤勇者 - 陈奕迅"
    """
    match = re.match(r"(.+)\s*-\s*(.+)", text)
    if match:
        title = match.group(1).strip()
        artist = match.group(2).strip()
        return title, artist
    return None, None

def netease_music_search_id(title, artist=None):
    """
    使用网易云音乐搜索接口，返回歌曲ID
    """
    keyword = f"{title} {artist}" if artist else title
    url = "https://music.163.com/api/search/get/web"
    params = {
        "s": keyword,
        "type": 1,
        "limit": 1,
        "offset": 0,
        "csrf_token": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Referer": "https://music.163.com/"
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        text = resp.text
        # 正则提取 song id
        match = re.search(r"search_tab_song::(\d+)::", text)
        if match:
            return match.group(1)
        else:
            print("未找到歌曲ID")
            return None
    except Exception as e:
        print("搜索请求失败:", e)
        return None

def netease_music_detail(song_id):
    """
    使用歌曲 ID 获取完整歌曲信息，包括高清封面（可选）
    """
    url = f"https://music.163.com/api/song/detail?ids=[{song_id}]"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Referer": "https://music.163.com/"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        songs = data.get("songs", [])
        if songs:
            return songs[0]
        else:
            print("未找到歌曲详情")
            return None
    except Exception as e:
        print("获取歌曲详情失败:", e)
        print("返回内容前200字符:", resp.text[:200])
        return None

def get_track_info(now_playing_text):
    """
    获取完整的歌曲信息，包括封面（如果没有则为 None）
    """
    title, artist = parse_now_playing(now_playing_text)
    if not title or not artist:
        print("解析失败：无法识别歌曲和歌手")
        return None

    # 搜索歌曲 ID
    song_id = netease_music_search_id(title, artist)
    if not song_id:
        return None

    # 获取歌曲详情
    song_json = netease_music_detail(song_id)
    if not song_json:
        return None

    # 封面处理：有就加参数，没有就 None
    cover_url = song_json.get("album", {}).get("picUrl")
    cover_url = cover_url + "?param=500y500" if cover_url else None

    track_data = {
        "title": song_json.get("name"),
        "author": " / ".join([s.get("name") for s in song_json.get("artists", [])]),
        "album": song_json.get("album", {}).get("name"),
        "duration": song_json.get("duration") // 1000 if song_json.get("duration") else 0,
        "songmid": str(song_json.get("id")),
        "cover": cover_url
    }

    return track_data

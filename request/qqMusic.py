import re
import requests
import json

def parse_now_playing(text):
    """
    解析 AppleScriptFetcher 的输出，返回 title 和 artist
    输入格式示例: "Lay By Me - Ruben"
    """
    match = re.match(r"(.+)\s*-\s*(.+)", text)
    if match:
        title = match.group(1).strip()
        artist = match.group(2).strip()
        return title, artist
    return None, None

def qq_music_search(title, artist=None):
    """
    使用 QQ 音乐搜索接口，返回 JSON 的歌曲信息
    """
    keyword = f"{title} {artist}"
    url = f"http://c.y.qq.com/soso/fcgi-bin/client_search_cp?w={keyword}&p=1&n=5&cr=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Referer": "https://y.qq.com/portal/search.html"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp_text = resp.text.strip()
    except requests.RequestException as e:
        print("请求失败:", e)
        return None

    # 去掉 callback() 包裹
    if resp_text.startswith("callback(") and resp_text.endswith(")"):
        resp_text = resp_text[9:-1]

    # 尝试解析 JSON
    try:
        data = json.loads(resp_text)
    except json.JSONDecodeError:
        print("解析失败，返回内容前500字符：", resp_text[:500])
        return None

    # 提取歌曲列表
    songs = data.get("data", {}).get("song", {}).get("list", [])
    if not songs:
        return None

    # 精确匹配：先匹配歌名 + 歌手
    title_clean = title.lower().replace(" ", "")
    artist_clean = artist.lower().replace(" ", "")
    for song in songs:
        song_title = song.get("songname", "").lower().replace(" ", "")
        singers = [s.get("name", "").lower().replace(" ", "") for s in song.get("singer", [])]
        if song_title == title_clean and any(artist_clean in s for s in singers):
            return song

    # 如果没有完全匹配，则返回第一首
    return songs[0]

def get_track_info(now_playing_text):
    title, artist = parse_now_playing(now_playing_text)
    if not title or not artist:
        return None

    song_json = qq_music_search(title, artist)
    if not song_json:
        return None

    # 封面 URL
    album_mid = song_json.get("albummid")
    cover_url = f"https://y.qq.com/music/photo_new/T002R300x300M000{album_mid}_1.jpg" if album_mid else "default_cover.png"

    track_data = {
        "title": song_json.get("songname"),
        "author": " / ".join([s.get("name") for s in song_json.get("singer", [])]),
        "album": song_json.get("albumname"),
        "cover": cover_url,
        "duration": song_json.get("interval"),
        "songmid": song_json.get("songmid"),
    }
    return track_data

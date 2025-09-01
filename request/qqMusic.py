import requests
import json

def search_qqmusic(keyword, n=5):
    """
    搜索 QQ 音乐歌曲
    :param keyword: 搜索关键词
    :param n: 返回最多歌曲数量
    :return: 歌曲信息列表，每个元素为 dict
    """
    url = f"http://c.y.qq.com/soso/fcgi-bin/client_search_cp?w={keyword}&p=1&n={n}&cr=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Host": "c.y.qq.com",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    resp = requests.get(url, headers=headers, timeout=10)
    text = resp.text

    # 去掉 callback(...) 包裹
    if text.startswith("callback(") and text.endswith(")"):
        text = text[9:-1]

    data = json.loads(text)

    if data.get("code") != 0:
        raise Exception("QQ 音乐歌曲信息获取失败")

    songs = data.get("data", {}).get("song", {}).get("list", [])
    tracks = []

    for song in songs:
        title = song.get("songname")
        authors = [s["name"] for s in song.get("singer", [])]
        author = " / ".join(authors)
        album = song.get("albumname")
        album_mid = song.get("albummid")
        duration = song.get("interval")
        song_id = song.get("songmid")
        cover = f"https://y.qq.com/music/photo_new/T002R500x500M000{album_mid}_1.jpg"

        track = {
            "title": title,
            "author": author,
            "album": album,
            "cover": cover,
            "duration": duration,
            "id": song_id
        }
        tracks.append(track)

    return tracks

# 测试
if __name__ == "__main__":
    keyword = "wild"
    results = search_qqmusic(keyword)
    for i, track in enumerate(results, 1):
        print(f"{i}. {track}")

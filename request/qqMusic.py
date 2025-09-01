import requests

def search_qqmusic(keyword):
    url = f"http://c.y.qq.com/soso/fcgi-bin/client_search_cp?w={keyword}&p=1&n=2&cr=1"

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

    data = resp.json()

    if data.get("code") != 0:
        raise Exception("QQ 音乐歌曲信息获取失败")

    songs = data["data"]["song"]["list"]
    song = songs[0]

    # 获取主要信息
    title = song["songname"]
    authors = [s["name"] for s in song["singer"]]
    author = " / ".join(authors)
    album = song["albumname"]
    album_mid = song["albummid"]
    duration = song["interval"]
    song_id = song["songmid"]
    cover = f"https://y.qq.com/music/photo_new/T002R500x500M000{album_mid}_1.jpg"

    track = {
        "title": title,
        "author": author,
        "album": album,
        "cover": cover,
        "duration": duration,
        "id": song_id
    }

    return track


# 测试
if __name__ == "__main__":
    keyword = "稻香"
    info = search_qqmusic(keyword)
    print(info)

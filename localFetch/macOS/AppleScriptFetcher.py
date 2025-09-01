import subprocess
import time

def get_qqmusic_now_playing():
    apple_script = '''
    tell application "System Events"
        -- 获取 QQ音乐窗口
        tell process "QQMusic"
            if exists window 1 then
                set win to window 1
                try
                    -- QQ音乐窗口里通常歌曲名在 static text 1，歌手在 static text 2
                    set song_name to value of static text 1 of win
                    set artist_name to value of static text 2 of win
                on error
                    set song_name to "Unknown"
                    set artist_name to "Unknown"
                end try
            else
                set song_name to "No window"
                set artist_name to "No window"
            end if
        end tell
    end tell
    return song_name & " - " & artist_name
    '''
    result = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True)
    return result.stdout.strip()

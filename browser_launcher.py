import webbrowser
import subprocess
import platform
import os

#global chrome_process

def open_chrome(url="http://localhost:8080/player.html"):
    """
    Chrome ブラウザで指定された URL を自動的に開く関数。

    Args:
        url (str): 開く URL（デフォルトは MPEG-DASH プレイヤーの URL）。
    """
    global chrome_process
    chrome_path = ""

    if platform.system() == "Windows":
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    elif platform.system() == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif platform.system() == "Linux":
        chrome_path = "/usr/bin/google-chrome"

    if os.path.exists(chrome_path):
        print(f'Chrome起動中...\n')
        chrome_process = subprocess.Popen([chrome_path, "--enable-logging", "--v=1", url])
    else:
        print(f'Chromeが見つかりません')
        chrome_process = webbrowser.open(url)

def close_chrome():
    global chrome_process
    if chrome_process:
        chrome_process.terminate()
        print("Chrome タブを閉じました")

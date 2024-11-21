import http.server
import socketserver
import os

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def setup_web_server(directory="segments", port=8080):
    """
    MPD ファイルと動画セグメントを提供するローカル HTTP サーバを設定します。

    Args:
        directory (str): 配信するファイルが格納されているディレクトリ。
        port (int): サーバのポート番号。
    """
    # 配信ディレクトリに移動
    os.chdir(directory)

    # HTTP ハンドラの設定
    #handler = http.server.SimpleHTTPRequestHandler
    handler = CustomHandler

    # サーバの起動
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving HTTP on port {port} (http://localhost:{port}/) ...")
        print(f"MPD ファイルの URL: http://localhost:{port}/manifest.mpd")
        httpd.serve_forever()

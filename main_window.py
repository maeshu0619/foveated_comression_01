"""
セグメントが独立してデコードできるため、用意する動画のフレームはIフレームのみにし、P,Bフレームは取り扱わないのが
最も好ましい。しかし、現在は全てのフレームを参照するようになっている。
"""

import pygame
import cv2
import threading
import os
import browser_launcher
import numpy as np
from foveated_compression import merge_frame
#from cursor import cursor_bunnish, cursor_image, cursor_position 
from mpeg_dash import frame_segmented, generate_mpd
from mpeg_server import setup_web_server
from client_player import create_client_player
from browser_launcher import open_chrome

class MainWindow:
    def __init__(self, low_res_path, med_res_path, high_res_path):
        self.low_cap = cv2.VideoCapture(low_res_path)
        self.med_cap = cv2.VideoCapture(med_res_path)
        self.high_cap = cv2.VideoCapture(high_res_path)

        pygame.init()
        self.window_width, self.window_height = 960, 540
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Foveated Compression Video Experiment with H.264 Compression System")

        self.cursor_image = pygame.image.load("Assets/Red+.png")
        self.cursor_rect = self.cursor_image.get_rect()
        pygame.mouse.set_visible(False)

        # MPEG-DASH 用の初期設定
        self.segment_dir = os.path.abspath("segments/segmented_video")  # 絶対パスを設定
        os.makedirs(self.segment_dir, exist_ok=True)
        print(f"セグメントディレクトリ: {self.segment_dir}")

        self.fps = 30
        self.frame_counter = 0

        # サーバとブラウザを別スレッドで起動
        self.start_web_server()
        self.start_browser()

    def start_web_server(self):
        server_thread = threading.Thread(target=setup_web_server, args=("segments",), daemon=True)
        server_thread.start()

    def start_browser(self):
        browser_thread = threading.Thread(target=open_chrome, args=("http://localhost:8080/player.html",), daemon=True)
        browser_thread.start()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            ret_low, frame_low = self.low_cap.read()
            ret_med, frame_med = self.med_cap.read()
            ret_high, frame_high = self.high_cap.read()

            if not (ret_low and ret_med and ret_high):
                break

            frame_low = cv2.resize(frame_low, (self.window_height, self.window_width))
            frame_med = cv2.resize(frame_med, (self.window_height, self.window_width))
            frame_high = cv2.resize(frame_high, (self.window_height, self.window_width))

            # フレームの回転と反転処理
            frame_low = cv2.rotate(frame_low, cv2.ROTATE_90_CLOCKWISE)
            frame_med = cv2.rotate(frame_med, cv2.ROTATE_90_CLOCKWISE)
            frame_high = cv2.rotate(frame_high, cv2.ROTATE_90_CLOCKWISE)

            frame_low = cv2.flip(frame_low, 1)
            frame_med = cv2.flip(frame_med, 1)
            frame_high = cv2.flip(frame_high, 1)

            # 合成フレーム作成
            combined_frame = merge_frame(frame_low, frame_med, frame_high, 0, 0)

            # フレームをセグメント化
            frame_segmented(combined_frame, self.fps, self.segment_dir)
            if self.frame_counter >= self.fps * 2:
                generate_mpd(segment_dir=self.segment_dir, mpd_path=os.path.join("segments", "manifest.mpd"))
                self.frame_counter = 0

            self.frame_counter += 1
            clock.tick(60)


        self.low_cap.release()
        self.med_cap.release()
        self.high_cap.release()
        pygame.quit()
        # 終了時にブラウザを閉じる
        browser_launcher.close_chrome()

        """
        # Web サーバの起動とクライアントプレイヤーの作成
        create_client_player(output_dir=self.segment_dir)
        setup_web_server(directory=self.segment_dir)
        open_chrome("http://localhost:8080/player.html")
        """
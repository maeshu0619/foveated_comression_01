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
        pygame.mouse.set_visible(False)  # システムカーソルを非表示にする

        # MPEG-DASH 用の初期設定
        self.segment_dir = "segments"
        self.fps = 30
        self.frame_counter = 0
        '''
        # セグメントディレクトリの作成
        segment_dir="segmented_video"
        if not os.path.exists(segment_dir):
            os.makedirs(segment_dir)
            print(f"ディレクトリを作成しました: {segment_dir}")
        else:
            print(f"ディレクトリが既に存在しています： {segment_dir}")
        '''

        # サーバとブラウザを別スレッドで起動
        self.start_web_server()
        self.start_browser()

    def start_web_server(self):
        server_thread = threading.Thread(target=setup_web_server, args=(self.segment_dir,), daemon=True)
        server_thread.start()

    def start_browser(self):
        browser_thread = threading.Thread(target=open_chrome, args=("http://localhost:8080/player.html",), daemon=True)
        browser_thread.start()

    def run(self):
        clock = pygame.time.Clock()
        running = True

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

            # フレームの180度回転（上下左右の反転に対応）
            frame_low = cv2.rotate(frame_low, cv2.ROTATE_180)
            frame_med = cv2.rotate(frame_med, cv2.ROTATE_180)
            frame_high = cv2.rotate(frame_high, cv2.ROTATE_180)

            # OpenCVからPygameに変換する前に、フレームを左右反転
            frame_low = np.ascontiguousarray(np.fliplr(frame_low))
            frame_med = np.ascontiguousarray(np.fliplr(frame_med))
            frame_high = np.ascontiguousarray(np.fliplr(frame_high))

            # OpenCV から Pygame Surface に変換
            frame_low = cv2.cvtColor(frame_low, cv2.COLOR_BGR2RGB)
            frame_med = cv2.cvtColor(frame_med, cv2.COLOR_BGR2RGB)
            frame_high = cv2.cvtColor(frame_high, cv2.COLOR_BGR2RGB)

            surface_low = pygame.surfarray.make_surface(frame_low)
            surface_med = pygame.surfarray.make_surface(frame_med)
            surface_high = pygame.surfarray.make_surface(frame_high)

            cursor_x, cursor_y = pygame.mouse.get_pos()

            try:
                #print(f'Frame merging done')
                combined_frame = merge_frame(frame_low, frame_med, frame_high, cursor_y, cursor_x)  
                #combined_frame = cv2.cvtColor(combined_frame, cv2.COLOR_BGR2RGB)                    # 合成後のフレームの色空間変換/不要
            except Exception as e:
                print(f"Error during frame merging: {e}\n")
                break

            #Main Windowに動画を出力
            #combined_frame = cv2.cvtColor(combined_frame, cv2.COLOR_BGR2RGB)        #動画が青白くなるのを防ぐ/不要
            surface = pygame.surfarray.make_surface(combined_frame)
            self.screen.blit(surface, (0, 0))
            self.cursor_rect.center = (cursor_x, cursor_y)
            self.screen.blit(self.cursor_image, self.cursor_rect)
            pygame.display.flip()

            # フレームセグメントの生成
            self.frame_counter += 1
            frame_segmented(combined_frame, self.fps)

            # 2秒ごとに MPD ファイルを生成
            # 2秒ごとに MPD ファイルを更新し、プレイヤーに再読み込みを促す
            if self.frame_counter >= self.fps * 2:
                generate_mpd(segment_dir=self.segment_dir)
                # プレイヤーの再読み込みを促すリクエスト
                os.system("curl http://localhost:8080/manifest.mpd -s > nul")
            self.frame_counter = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

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
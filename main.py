import pygame
import multiprocessing
import os
from experiment import debug_timer
from h264_compression import h264_compression
from main_window import MainWindow
from monitor_window import MonitorWindow
from plot_window import PlotWindow
from browser_launcher import close_chrome

def start_monitor_window(monitor_queue):
    monitor = MonitorWindow(monitor_queue)
    monitor.render()

def start_plot_window(monitor_queue):
    plot = PlotWindow(monitor_queue)
    plot.render()

if __name__ == "__main__":
    pygame.init()
    monitor_queue = multiprocessing.Queue()
    input_video = "Assets/Snow.mp4"

    # 初期カーソル位置の設定
    cursor_x, cursor_y = 480, 270

    try:
        # フォビエイテッド圧縮を実行して、低・中・高解像度の動画ファイルを取得
        low_res_path, med_res_path, high_res_path = h264_compression(input_video)
        print(f"Foveated compressing done")
    except Exception as e:
        # 圧縮に失敗した場合はオリジナルの動画を使用
        low_res_path = med_res_path = high_res_path = input_video
        print(f"Foveated compression failed: {e}")

    # Monitor と Plot ウィンドウのプロセスを開始
    monitor_process = multiprocessing.Process(target=start_monitor_window, args=(monitor_queue,))
    monitor_process.start()

    plot_process = multiprocessing.Process(target=start_plot_window, args=(monitor_queue,))
    plot_process.start()

    
    # セグメントディレクトリの作成
    segment_dir="segments/segmented_video"
    if not os.path.exists(segment_dir):
        os.makedirs(segment_dir)
        print(f"ディレクトリを作成しました: {segment_dir}")
    else:
        print(f"ディレクトリが既に存在しています： {segment_dir}")
    # MainWindow の初期化と実行
    try:
        main_window_instance = MainWindow(low_res_path, med_res_path, high_res_path)
        main_window_instance.run()
    except Exception as e:
        print(f"Error in Main Window: {e}")

    # プロセスの終了
    monitor_process.terminate()
    plot_process.terminate()
    pygame.quit()
    close_chrome()
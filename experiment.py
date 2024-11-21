import time

def debug_timer(func):
    """
    デバッグ用の時間計測デコレータ関数
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 開始時間を記録
        result = func(*args, **kwargs)  # 関数を実行
        end_time = time.time()  # 終了時間を記録
        elapsed_time = end_time - start_time  # 実行時間を計算
        print(f"関数 '{func.__name__}' の実行時間: {elapsed_time:.6f} 秒")
        return result
    return wrapper

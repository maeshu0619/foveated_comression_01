"""
αブレンドによる高解像度エリアの合成は、動画の合成数が増加するにつれて
輝度が高くなるバグを修正することができるが、計算コストが高いため、推奨されない。
result=src1×α+src2×β+γ

    # 高解像度エリアの合成（アルファブレンド）
    high_alpha = high_mask / 255.0
    med_alpha = med_mask / 255.0 * (1.0 - high_alpha)
    low_alpha = 1.0 - high_alpha - med_alpha

    # 合成フレームの計算
    combined_frame = (
        frame_high * high_alpha +
        frame_med * med_alpha +
        frame_low * low_alpha
    ).astype(np.uint8)

よって現在は、条件分岐を使って合成を行ている。
"""
import cv2
import numpy as np

def merge_frame(frame_low, frame_med, frame_high, cursor_x, cursor_y):
    # マスクの初期化
    med_mask = np.zeros((frame_low.shape[0], frame_low.shape[1]), dtype=np.uint8)
    high_mask = np.zeros((frame_low.shape[0], frame_low.shape[1]), dtype=np.uint8)

    # マスクの半径設定
    med_radius = 200
    high_radius = 100

    # マスクの作成（円形）
    cv2.circle(med_mask, (cursor_x, cursor_y), med_radius, 255, -1)
    cv2.circle(high_mask, (cursor_x, cursor_y), high_radius, 255, -1)

    # 条件分岐を使って合成
    combined_frame = np.where(
        high_mask[..., np.newaxis] > 0,
        frame_high,
        np.where(med_mask[..., np.newaxis] > 0, frame_med, frame_low)
    )

    return combined_frame

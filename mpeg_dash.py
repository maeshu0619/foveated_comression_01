"""
MPEG-DASH SRD based 360 VR Tiled Streaming System for Foveated Rendering
author: Hyun Wook Kim;Jin Wook Yang;Jae Young Yang;Jun Hwan Jang;Woo Chool Park
Year: 2018 | Conference Paper | Publisher: IEEE
"""

import cv2
import os
import datetime
import traceback
import xml.etree.ElementTree as ET

# フレームバッファとセグメントインデックスをグローバル変数として定義
frame_buffer = []
segment_index = 0

def frame_segmented(combined_frame, fps, segment_dir="segmented_video", segment_duration=2):
    """
    合成フレームをセグメント化し、MPEG-DASH 用のセグメントとして保存する関数。

    Args:
        combined_frame (np.ndarray): 合成されたフレーム。
        fps (int): 動画のフレームレート。
        segment_dir (str): セグメントファイルを保存するディレクトリ。
        segment_duration (int): セグメントの長さ（秒単位）。
    """
    global frame_buffer, segment_index

    '''
    # セグメントディレクトリの作成
    if not os.path.exists(segment_dir):
        os.makedirs(segment_dir)
        print(f"ディレクトリを作成しました: {segment_dir}")
    else:
        print(f"ディレクトリが既に存在しています： {segment_dir}")
    '''
    
    # 2秒分のフレーム数を計算
    frames_per_segment = fps * segment_duration
    #print(f"{frames_per_segment}")

    # フレームをバッファに追加
    frame_buffer.append(combined_frame)
    #print(f"{len(frame_buffer)}")
    #print(f"フレームバッファの長さ: {len(frame_buffer)}/{frames_per_segment}")

    # バッファが2秒分に達した場合、セグメントを保存
    if len(frame_buffer) >= frames_per_segment:
        segment_path = os.path.join(segment_dir, f"segment_{segment_index:04d}.mp4")
        print(f"セグメントを保存中: {segment_path}")
        height, width, _ = combined_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        try:
            out = cv2.VideoWriter(segment_path, fourcc, fps, (width, height))

            if not out.isOpened():
                print(f"VideoWriter の初期化に失敗しました: {segment_path}")
                return False

            for frame in frame_buffer:
                out.write(frame)

            out.release()
            print(f"セグメント {segment_index} を保存しました: {segment_path}")
            generate_mpd(segment_dir=segment_dir)  # MPD ファイルの即時更新

        except Exception as e:
            error_message = traceback.format_exc()
            print(f"セグメント {segment_index} の保存に失敗しました: {segment_path}")
            print(f"エラーの詳細: {error_message}")

        frame_buffer.clear()
        segment_index += 1
        return True
    
        '''
        out = cv2.VideoWriter(segment_path, fourcc, fps, (width, height))

        # バッファ内のフレームを動画ファイルに書き込み
        for frame in frame_buffer:
            out.write(frame)
        # セグメントの書き込み後にフラッシュを追加
        out.flush()  # 書き込みのフラッシュ
        out.release()
        print(f"セグメント {segment_index} を保存しました: {segment_path}")
        
        # バッファのクリアとインデックスの更新
        frame_buffer.clear()
        segment_index += 1
        return True  # セグメントの書き込み完了を通知
        '''
    return False


def generate_mpd(segment_dir="segments", mpd_path="manifest.mpd", fps=30, resolution="960x540", bitrate="1500k"):
    """
    MPEG-DASH の MPD ファイルを生成する関数。

    Args:
        segment_dir (str): セグメントファイルが保存されているディレクトリ。
        mpd_path (str): 出力する MPD ファイルのパス。
        fps (int): 動画のフレームレート。
        resolution (str): 動画の解像度（例: "960x540"）。
        bitrate (str): ビットレート（例: "1500k"）。
    """
    import xml.etree.ElementTree as ET
    from datetime import datetime

    # MPD ファイルのルート要素
    mpd = ET.Element("MPD", attrib={
        "xmlns": "urn:mpeg:dash:schema:mpd:2011",
        "profiles": "urn:mpeg:dash:profile:isoff-on-demand:2011",
        "type": "dynamic",
        "minBufferTime": "PT1.5S",
        "minimumUpdatePeriod": "PT2S",
        "availabilityStartTime": datetime.utcnow().isoformat() + "Z"
    })

    # Period 要素の追加
    #period = ET.SubElement(mpd, "Period", attrib={"duration": "PT2M"})
    #period = ET.SubElement(mpd, "Period")
    period = ET.SubElement(mpd, "Period", attrib={"id": "1"})

    # AdaptationSet 要素の追加
    adaptation_set = ET.SubElement(period, "AdaptationSet", attrib={
        "mimeType": "video/mp4",
        "codecs": "avc1.42E01E",
        "width": resolution.split("x")[0],
        "height": resolution.split("x")[1],
        "frameRate": str(fps),
        "bandwidth": bitrate
    })

    # Representation 要素の追加
    representation = ET.SubElement(adaptation_set, "Representation", attrib={
        "id": "1",
        "bandwidth": bitrate,
        "width": resolution.split("x")[0],
        "height": resolution.split("x")[1],
        "frameRate": str(fps)
    })
    
    segment_list = ET.SubElement(representation, "SegmentList", attrib={
        "timescale": str(fps),
        "duration": str(fps * 2)
    })

    segment_files = sorted([f for f in os.listdir(segment_dir) if f.endswith(".mp4")])
    for segment_file in segment_files:
        ET.SubElement(segment_list, "SegmentURL", attrib={"media": segment_file})

    tree = ET.ElementTree(mpd)
    tree.write(mpd_path, xml_declaration=True, encoding="utf-8")
    print(f"MPD ファイルを生成しました: {mpd_path}")
import cv2
import os
import subprocess
import traceback
import datetime
import xml.etree.ElementTree as ET

frame_buffer = []
segment_index = 0


def frame_segmented(combined_frame, fps, segment_dir="segments/segmented_video", segment_duration=2):
    """
    合成フレームをセグメント化し、90度時計回りに回転して左右反転し、H.264/AAC形式でエンコードして保存します。

    Args:
        combined_frame (np.ndarray): 合成されたフレーム。
        fps (int): 動画のフレームレート。
        segment_dir (str): セグメントファイルを保存するディレクトリ。
        segment_duration (int): セグメントの長さ（秒単位）。
    """
    global frame_buffer, segment_index

    # セグメントディレクトリを絶対パスに変換
    segment_dir = os.path.abspath(segment_dir)
    os.makedirs(segment_dir, exist_ok=True)  # ディレクトリを作成

    # 回転と反転の処理
    processed_frame = cv2.rotate(combined_frame, cv2.ROTATE_90_CLOCKWISE)  # 90度時計回り
    processed_frame = cv2.flip(processed_frame, 1)  # 左右反転

    frames_per_segment = fps * segment_duration
    frame_buffer.append(processed_frame)

    # フレームが規定数に達したらセグメントを保存
    if len(frame_buffer) >= frames_per_segment:
        raw_segment_path = os.path.join(segment_dir, f"segment_{segment_index:04d}_raw.mp4")
        encoded_segment_path = os.path.join(segment_dir, f"segment_{segment_index:04d}.mp4")

        # OpenCVを使って未エンコードの動画を保存
        try:
            height, width, _ = frame_buffer[0].shape
            out = cv2.VideoWriter(raw_segment_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
            for frame in frame_buffer:
                out.write(frame)
            out.release()

            print(f"未エンコードセグメントを保存しました: {raw_segment_path}")

            # ファイルの存在確認
            if not os.path.exists(raw_segment_path):
                raise FileNotFoundError(f"未エンコードファイルが見つかりません: {raw_segment_path}")
        except Exception as e:
            print(f"セグメント保存エラー: {raw_segment_path}")
            print(traceback.format_exc())
            frame_buffer.clear()
            return False

        # ffmpegを使ってH.264/AAC形式にエンコード
        try:
            # ffmpegでH.264/AACに変換 + 90度回転
            command = [
                "ffmpeg",
                "-i", raw_segment_path,
                "-vf", "transpose=1",  # 90度時計回りに回転
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-strict", "experimental",
                encoded_segment_path,
                "-y"
            ]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # ffmpegのエラーチェック
            if result.returncode != 0:
                print(f"ffmpegエラー: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, command)

            print(f"エンコード済みセグメントを保存しました: {encoded_segment_path}")
        except Exception as e:
            print(f"エンコード中にエラーが発生しました: {encoded_segment_path}")
            print(traceback.format_exc())
        finally:
            # 一時的な未エンコードファイルを削除
            if os.path.exists(raw_segment_path):
                os.remove(raw_segment_path)

        # フレームバッファをクリアし、次のセグメントの準備
        frame_buffer.clear()
        segment_index += 1
        return True

    return False
def generate_mpd(segment_dir="segments/segmented_video", mpd_path="segments/manifest.mpd", fps=30, resolution="960x540", bitrate="1500k", total_duration=24):
    segment_dir = os.path.abspath(segment_dir)
    mpd_path = os.path.abspath(mpd_path)
    os.makedirs(os.path.dirname(mpd_path), exist_ok=True)

    # 動画全体の長さを計算 (Snow.mp4: 24秒)
    total_duration_frames = total_duration * fps

    mpd = ET.Element("MPD", attrib={
        "xmlns": "urn:mpeg:dash:schema:mpd:2011",
        "profiles": "urn:mpeg:dash:profile:isoff-on-demand:2011",
        "type": "dynamic",
        "minBufferTime": "PT1.5S",
        "availabilityStartTime": datetime.datetime.utcnow().isoformat() + "Z"
    })

    period = ET.SubElement(mpd, "Period", attrib={"id": "1"})
    adaptation_set = ET.SubElement(period, "AdaptationSet", attrib={
        "mimeType": "video/mp4",
        "codecs": "avc1.42E01E",
        "width": resolution.split("x")[0],
        "height": resolution.split("x")[1],
        "frameRate": str(fps),
        "bandwidth": bitrate
    })

    representation = ET.SubElement(adaptation_set, "Representation", attrib={
        "id": "1",
        "bandwidth": bitrate,
        "width": resolution.split("x")[0],
        "height": resolution.split("x")[1],
        "frameRate": str(fps)
    })

    segment_list = ET.SubElement(representation, "SegmentList", attrib={
        "timescale": str(fps),
        "duration": str(total_duration_frames)
    })

    segment_files = sorted([f for f in os.listdir(segment_dir) if f.endswith(".mp4") and not f.endswith("_raw.mp4")])
    for segment_file in segment_files:
        ET.SubElement(segment_list, "SegmentURL", attrib={"media": f"segmented_video/{segment_file}"})

    tree = ET.ElementTree(mpd)
    tree.write(mpd_path, xml_declaration=True, encoding="utf-8")
    print(f"MPD ファイルを生成しました: {mpd_path}")

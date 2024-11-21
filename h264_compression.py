import subprocess

def h264_compression(input_video):
    low_res_output = "h264_outputs/low_res.mp4"
    med_res_output = "h264_outputs/med_res.mp4"
    high_res_output = "h264_outputs/high_res.mp4"

    subprocess.run(["mkdir", "-p", "h264_outputs"], shell=True)

    low_res_cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", "scale=480:270", "-c:v", "libx264", "-crf", "30", "-preset", "ultrafast",
        "-tune", "zerolatency", low_res_output
    ]

    med_res_cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", "scale=640:360", "-c:v", "libx264", "-crf", "25", "-preset", "ultrafast",
        "-tune", "zerolatency", med_res_output
    ]

    high_res_cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", "scale=1920:1080", "-c:v", "libx264", "-crf", "5", "-preset", "ultrafast",
        "-tune", "zerolatency", high_res_output
    ]


    return low_res_output, med_res_output, high_res_output

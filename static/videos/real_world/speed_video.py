import cv2
import subprocess
import os

def accelerate_video_true_no_drop(input_path, output_path, speed_factor=2):
    temp_video = "temp_with_text.mp4"

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("无法打开视频")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 先把每帧写上文字并保存成一个临时视频
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, f"{speed_factor}x",
                    (10, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 3,
                    (0, 255, 0), 4)

        out.write(frame)

    cap.release()
    out.release()

    # 再用 ffmpeg 调整 PTS（关键步骤：不丢帧，但加速）
    cmd = [
        "ffmpeg",
        "-y",
        "-i", temp_video,
        "-filter:v", f"setpts=PTS/{speed_factor}",
        "-an",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    os.remove(temp_video)

    print("完成输出:", output_path)

accelerate_video_true_no_drop("msra_pi0_press_red_button.mp4", "msra_pi0_press_red_button_speed.mp4", speed_factor=4)

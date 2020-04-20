import concurrent.futures
import os
import subprocess
import uuid
from shutil import copyfile, rmtree
from gentle_handler import process_with_gentle, process_timestamps, timestamps_to_frames
from image_handler import pull_image, draw_frame
from transcript import Transcript


def auto_vid_maker(transcript_path: str, audio_path: str, video_name: str, fps: int = 30) -> str:
    """Creates a video of images synced with a transcript and audio
    recording.

    Parameters:
    transcript_path (str): Path to annotated transcript.
    audio_path (str): Path to audio recording of transcript.

    Returns:
    vid_path (str): Path to video.
    """
    transcript: Transcript = Transcript(transcript_path)

    image_dir: str = str(uuid.uuid4())
    os.mkdir(image_dir)
    copyfile("beginning_image.jpg", os.path.join(image_dir, "beginning_image.jpg"))

    t0 = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(lambda x: pull_image(x[0], image_dir, mode=x[1], threads=15),
                     [(keywords, topic[keywords]) for topic in transcript.topics for keywords in topic])

    print(f"DOWNLOAD TIME: {time.time() - t0}")

    gentle_json = process_with_gentle(transcript.cleaned_transcript, audio_path)
    timestamps = process_timestamps(transcript, gentle_json)
    time_frames = timestamps_to_frames(timestamps, audio_path, fps=fps)
    frames_dir = os.path.join(image_dir, "frames")
    os.mkdir(frames_dir)

    t0 = time.time()

    for phrase in time_frames:
        if phrase != "beginning_image":
            topic = list(transcript.parsed_transcript[phrase].keys())[0]
        else:
            topic = phrase
        frame_path = draw_frame(os.path.join(image_dir, topic + ".jpg"),
                                phrase, frames_dir,
                                str(time_frames[phrase]["start"]) + ".jpg")

        for frame_num in range(time_frames[phrase]["start"] + 1, time_frames[phrase]["end"] + 1):
            copyfile(frame_path, os.path.join(frames_dir, str(frame_num) + ".jpg"))

    print(f"FRAME CREATION TIME: {time.time() - t0}")

    temp_vid = os.path.join(frames_dir, str(uuid.uuid4()) + ".mp4")
    cmd = f"ffmpeg -r {fps} -f image2 -s 800x600 -i {frames_dir}/%d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p {temp_vid}"
    subprocess.call(cmd, shell=True)
    subprocess.call(f"ffmpeg -i {audio_path} -i {temp_vid} {video_name}", shell=True)

    rmtree(image_dir)

    return os.path.abspath(video_name)


if __name__ == "__main__":
    import time
    t0 = time.time()
    auto_vid_maker("example_transcript.txt", "example_audio.wav", "example_video.mp4")
    print(time.time() - t0)
    # auto_vid_maker("test_transcript.txt", "test.wav", "my_test.mp4")


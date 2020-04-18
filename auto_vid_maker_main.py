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

    for topic in transcript.topics:
        for keywords in topic:
            pull_image(keywords, image_dir, mode=topic[keywords])

    gentle_json = process_with_gentle(transcript.cleaned_transcript, audio_path)
    timestamps = process_timestamps(transcript, gentle_json)
    time_frames = timestamps_to_frames(timestamps, audio_path, fps=fps)
    frames_dir = os.path.join(image_dir, "frames")
    os.mkdir(frames_dir)

    for phrase in time_frames:
        if phrase != "beginning_image":
            topic = list(transcript.parsed_transcript[phrase].keys())[0]
        else:
            topic = phrase
        for frame in range(time_frames[phrase]["start"], time_frames[phrase]["end"] + 1):
            print(draw_frame(os.path.join(image_dir, topic + ".jpg"),
                             phrase, os.path.join(image_dir, "frames"), str(frame) + ".jpg"))

    temp_vid = os.path.join(frames_dir, str(uuid.uuid4()) + ".mp4")
    cmd = f"ffmpeg -r {fps} -f image2 -s 800x600 -i {frames_dir}/%d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p {temp_vid}"
    subprocess.call(cmd, shell=True)
    subprocess.call(f"ffmpeg -i {audio_path} -i {temp_vid} {video_name}", shell=True)

    rmtree(image_dir)

    return os.path.abspath(video_name)


if __name__ == "__main__":
    while True:
        try:
            auto_vid_maker("test_transcript.txt", "test.wav", "full_test.mp4")
            break
        except:
            pass


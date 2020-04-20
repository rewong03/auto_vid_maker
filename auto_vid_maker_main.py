import argparse
import concurrent.futures
import os
import subprocess
import uuid
from shutil import copyfile, rmtree
from typing import Dict
from gentle_handler import process_timestamps, process_with_gentle, timestamps_to_frames
from image_handler import draw_frame, pull_image
from transcript import Transcript


def auto_vid_maker(transcript_path: str, audio_path: str, video_path: str, fps: int = 30,
                   threads: int = 15, silent: bool = False) -> str:
    """Creates a video of images synced with a transcript and audio
    recording.

    Parameters:
    transcript_path (str): Path to annotated transcript.
    audio_path (str): Path to audio recording of transcript.
    video_path (str): Location to create video.

    Returns:
    video_path (str): Path to video.
    """
    print("Parsing transcript...")
    transcript: Transcript = Transcript(transcript_path)

    image_dir: str = str(uuid.uuid4())
    os.mkdir(image_dir)
    copyfile("beginning_image.jpg", os.path.join(image_dir, "beginning_image.jpg"))

    print("Downloading images...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(lambda x: pull_image(x[0], image_dir, mode=x[1], threads=threads, silent=silent),
                     [(keywords, topic[keywords]) for topic in transcript.topics for keywords in topic])

    print("Processing transcript...")

    gentle_json: Dict = process_with_gentle(transcript.cleaned_transcript, audio_path)
    timestamps: Dict[str, Dict[str, float]] = process_timestamps(transcript, gentle_json)
    time_frames: Dict[str, Dict[str, int]] = timestamps_to_frames(timestamps, audio_path, fps=fps)
    frames_dir: str = os.path.join(image_dir, "frames")
    os.mkdir(frames_dir)

    print("Creating frames...")

    for phrase in time_frames:
        if phrase != "beginning_image":
            topic: str = list(transcript.parsed_transcript[phrase].keys())[0]
        else:
            topic: str = phrase
        frame_path: str = draw_frame(os.path.join(image_dir, topic + ".jpg"),
                                     phrase, frames_dir,
                                     str(time_frames[phrase]["start"]) + ".jpg")

        for frame_num in range(time_frames[phrase]["start"] + 1, time_frames[phrase]["end"] + 1):
            copyfile(frame_path, os.path.join(frames_dir, str(frame_num) + ".jpg"))

    print("Creating video...")

    temp_vid: str = os.path.join(frames_dir, str(uuid.uuid4()) + ".mp4")
    cmd: str = f"ffmpeg -r {fps} -f image2 -s 800x600 -i {frames_dir}/%d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p {temp_vid}"
    subprocess.call(cmd, shell=True)
    subprocess.call(f"ffmpeg -i {audio_path} -i {temp_vid} {video_path}", shell=True)

    rmtree(image_dir)

    return os.path.abspath(video_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a video of images from an annotated transcript and audio recording")

    parser.add_argument("transcript_path", type=str, help="Path to annotated transcript")
    parser.add_argument("audio_path", type=str, help="Path to .wav audio recording")
    parser.add_argument("video_path", type=str, help="Location to create video")
    parser.add_argument("--fps", required=False, type=int, default=30, help="FPS of video")
    parser.add_argument("--threads", required=False, type=int, default=15, help="No. threads to use to pull images")
    parser.add_argument("--verbose", required=False, type=bool, default=False, help="Whether to print pulling messages")

    args = parser.parse_args()
    print(auto_vid_maker(args.transcript_path, args.audio_path, args.video_path, fps=args.fps, threads=args.threads,
                         silent=not args.verbose))


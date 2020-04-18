import os
import uuid
from gentle_handler import process_with_gentle
from image_handler import pull_image
from transcript import Transcript


def auto_vid_maker(transcript_path: str, audio_path: str) -> str:
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

    for topic in transcript.topics:
        for keywords in topic:
            pull_image(keywords, image_dir, mode=topic[keywords])

    gentle_json = process_with_gentle(transcript.cleaned_transcript, audio_path)


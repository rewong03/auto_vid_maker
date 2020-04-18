import json
import math
import string
import tempfile
import wave
import contextlib
from subprocess import check_output
from typing import Dict, List
from transcript import Transcript


def process_with_gentle(cleaned_transcript: str, audio_path: str) -> Dict:
    """Processes a transcript and audio file with Gentle.

    Parameters:
    cleaned_transcript (str): A cleaned transcript.
    audio_path (str): Path to audio file.

    Returns:
    (dict): Json response from Gentle.
    """
    temp = tempfile.NamedTemporaryFile(mode="w+t")
    temp.write(cleaned_transcript)
    temp.seek(0)
    gentle_response: str = check_output(["python", "gentle/align.py",
                                        audio_path, temp.name])

    return json.loads(gentle_response)


#TODO: Make this more robust at checking bad gentle jsons
def process_timestamps(transcript_obj: Transcript, gentle_json: Dict) -> Dict:
    """Creates a dictionary of start and end times of phrases.

    Parameters:
    transcript_obj (Transcript Obj):
    gentle_json (dict): Dictionary of processed words from Gentle.

    Returns:
    timestamps (dict): A dictionary containing the start and end times of
    a phrase.
    """
    gentle_words: List[Dict] = gentle_json["words"]
    timestamps: Dict = {}

    for cleaned_phrase in transcript_obj.cleaned_phrases:
        words_in_phrase: List[str] = cleaned_phrase.split()
        phrase_timestamp: Dict = {}
        for idx, word in enumerate(words_in_phrase):
            gentle_word: Dict = gentle_words.pop(0)
            assert gentle_word["word"] == word.translate(str.maketrans('', '', string.punctuation)), "Word not found in Gentle json"

            if idx == 0:
                phrase_timestamp["start"] = round(gentle_word["start"], 2)
            elif idx == len(words_in_phrase) - 1:
                phrase_timestamp["end"] = round(gentle_word["end"], 2)

        timestamps[cleaned_phrase] = phrase_timestamp

    return timestamps


# Most likely will need to tweak in order to sync properly
def timestamps_to_frames(timestamps: Dict, audio_path: str, fps: int = 30) -> Dict:
    """Takes a timestamp dictionary as returned by process_timestamps
    and converts times to frames.

    Parameters:
    timestamps (dict): A dictionary containing the start and end times of
    a phrase.
    audio_path (str): Path to audio file used for transcript.
    fps (int): Frames per second.

    Returns:
    (dict)
    """
    with contextlib.closing(wave.open(audio_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    total_frames: int = math.ceil(duration * fps)
    current_no_frames: int = 0
    frames: Dict = {}
    phrases = list(timestamps.keys())

    for idx, phrase in enumerate(phrases):
        timestamp: Dict = timestamps[phrase]

        if idx == 0:
            beginning_frames: int = round(timestamp["start"] * fps)
            frames["beginning"] = {"start": 0, "end": beginning_frames}
            current_no_frames += beginning_frames

        if idx <= len(timestamps) - 2:
            num_frames: int = round((timestamps[phrases[idx + 1]]["start"] - timestamp["start"]) * fps)
            frames[phrase] = {"start": current_no_frames + 1, "end": current_no_frames + num_frames}
            current_no_frames += num_frames
        else:
            num_frames: int = round((timestamp["end"] - timestamp["start"]) * fps)
            frames[phrase] = {"start": current_no_frames + 1, "end": current_no_frames + num_frames}
            current_no_frames += num_frames

    frames["end"] = {"start": current_no_frames + 1, "end": total_frames}

    return frames


if __name__ == "__main__":
    my_transcript = Transcript("test_transcript.txt")
    gentle_json = process_with_gentle(my_transcript.cleaned_transcript, "test2.wav")
    print(gentle_json)
    print("____")
    t = process_timestamps(my_transcript, gentle_json)
    print(t)
    print(timestamps_to_frames(t, "test2.wav"))




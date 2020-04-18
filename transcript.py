import re
from typing import List, Dict


class Transcript:
    """A class for parsing annotated transcripts.

    Parameters:
    transcipt_path (str): Path to annotated transcript.
    """
    def __init__(self, transcript_path: str) -> None:
        self.raw_transcript: str = open(transcript_path).read()
        self.parsed_transcript: Dict[str, Dict[str, str]] = self.parse_transcript(self.raw_transcript)
        self.topics: List[str] = []

        for line in self.parsed_transcript:
            self.topics.extend(self.parsed_transcript[line])

        self.cleaned_transcript: str = self.clean_transcript(self.raw_transcript)

    @staticmethod
    def parse_transcript(raw_transcript: str) -> Dict[str, Dict[str, str]]:
        """Splits the raw transcript on newlines and slashes.

        Parameters:
        raw_transcript (str): A raw annotated transcript.

        Returns:
        parsed_transcript (dict(dict(str))): A dictionary containing each line
        in the transcript as well as the topics of each line.
        """
        parsed_transcript: Dict[str, Dict[str, str]] = {}
        newline_split: List[str] = raw_transcript.split("\n")
        slash_split: List[str] = []

        for line in newline_split:
            slash_split.extend(line.split(" / "))

        for line in slash_split:
            random_topic: List[str] = re.findall("\[.*\]", line)
            relevant_topic: List[str] = re.findall("\{.*\}", line)
            if random_topic and relevant_topic:
                raise ValueError("Can't have two topics in a line.")
            elif random_topic:
                parsed_transcript[line] = {random_topic[0][1: -1]: "random"}
            elif relevant_topic:
                parsed_transcript[line] = {random_topic[0][1: -1]: "relevant"}
            else:
                parsed_transcript[line] = {line, "random"}

        return parsed_transcript

    @staticmethod
    def clean_transcript(raw_transcript: str) -> str:
        """Removes brackets and slashes from a raw transcript.

        Parameters:
        raw_transcript (str): A raw annotated transcript.

        Returns:
        cleaned_transcript (str): A transcript without special characters.
        """
        clean_transcript: str = raw_transcript.replace("[", "").replace("]", "")
        clean_transcript = clean_transcript.replace("{", "").replace("}", "")
        clean_transcript = clean_transcript.replace(" / ", " ")

        return clean_transcript


if __name__ == "__main__":
    test_transcript = Transcript("test_transcript.txt")
    print(test_transcript.raw_transcript)
    print("____")
    print(test_transcript.parsed_transcript)
    print("____")
    print(test_transcript.cleaned_transcript)

import re
from typing import Dict, List


class Transcript:
    """A class for parsing annotated transcripts.

    Parameters:
    transcript_path (str): Path to annotated transcript.
    """
    def __init__(self, transcript_path: str) -> None:
        self.raw_transcript: str = open(transcript_path).read()
        self.raw_phrases: List[str] = self.split_phrases(self.raw_transcript)
        self.parsed_transcript: Dict[str, Dict[str, str]] = self.parse_transcript(self.raw_phrases)
        self.topics: List[Dict[str, str]] = []

        for line in self.parsed_transcript:
            self.topics.append(self.parsed_transcript[line])

        self.cleaned_phrases: List[str] = list(map(self.clean_phrase, self.raw_phrases))
        self.cleaned_transcript: str = " ".join(self.cleaned_phrases)

    @staticmethod
    def split_phrases(raw_transcript: str) -> List[str]:
        """Splits a raw transcript along newline and slashes.

        Parameters:
        raw_transcript (str): Raw text of a transcript.

        Returns:
        raw_phrases (list (str)): A list of phrases split on newline and slashes.
        """
        raw_phrases: List[str] = []

        for newline_split in raw_transcript.split("\n"):
            raw_phrases.extend(newline_split.split("/"))

        return list(map(lambda x: x.strip(), raw_phrases))

    def parse_transcript(self, raw_phrases: List[str]) -> Dict[str, Dict[str, str]]:
        """Extracts topics from raw phrases.

        Parameters:
        raw_transcript (str): A raw annotated transcript.

        Returns:
        parsed_transcript (dict(dict(str))): A dictionary containing each line
        in the transcript as well as the topics of each line.
        """
        parsed_transcript: Dict[str, Dict[str, str]] = {}

        for raw_phrase in raw_phrases:
            random_topic: List[str] = re.findall("\[.*\]", raw_phrase)
            relevant_topic: List[str] = re.findall("\{.*\}", raw_phrase)

            assert not(random_topic and relevant_topic), "Can't have two topics in a line."

            if random_topic:
                parsed_transcript[self.clean_phrase(raw_phrase)] = {random_topic[0][1: -1]: "random"}
            if relevant_topic:
                parsed_transcript[self.clean_phrase(raw_phrase)] = {relevant_topic[0][1: -1]: "relevant"}
            else:
                parsed_transcript[self.clean_phrase(raw_phrase)] = {self.clean_phrase(raw_phrase): "random"}

        return parsed_transcript

    @staticmethod
    def clean_phrase(raw_phrase: str) -> str:
        """Cleans brackets from a phrase.

        Parameters:
        raw_phrase (str): A raw phrase with brackets.

        Returns:
        clean_phrase (str): A phrase without any brackets.
        """
        clean_phrase: str = raw_phrase.replace("[", "").replace("]", "")
        clean_phrase = clean_phrase.replace("{", "").replace("}", "")

        return clean_phrase.strip()


if __name__ == "__main__":
    pass
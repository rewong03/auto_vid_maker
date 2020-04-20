# Automatic Image Video Generator
This is a python program that will take an annotated transcript and an audio file and 
create a video of images from Bing based on the transcript and sync it to the audio. Inspired by
[carykh's video](https://www.youtube.com/watch?v=Jr9sptoLvJU&feature=share).

## Installation
1. Clone this repository
        
        git clone https://github.com/rewong03/auto_vid_maker
        cd auto_vid_maker
        python3 virtualenv venv
        source venv/bin/activate

2. Install [Gentle](https://lowerquality.com/gentle/) (for Mac and Linux only). Please view the
   Gentle documentation for more installation information.
   
        git clone https://github.com/lowerquality/gentle
        cd gentle
        ./install.sh
        cd ..

3. Install the [Bing image downloader](https://github.com/ostrolucky/Bulk-Bing-Image-downloader).
        
        git clone https://github.com/ostrolucky/Bulk-Bing-Image-downloader 

## Annotated Transcript
The annotated transcript is crucial and helps the program determine which images to display and how
long to display them for. A topic is the image to show and a phrase is the length that the image should be 
shown for. Slashes and newlines determine phrases while brackets determine the topic.
Consider the following example:

        This is an [example] sentence.

The word `[example]` is the topic and an image of the word `example` will be shown for duration of the entire
sentence. To have two topics in a sentence, you can split the sentence into two phrases using slashes:

        This is [a topic], / this is [another topic].

The topic `[a topic]` will be shown for the duration of the phrase `This is a topic` while the topic
`another topic` will be shown for the rest of the sentence. Unfortunately slashes have to go after punctuation.
Phrases can also be split using a newline:
        
        This is [a topic].
        This is [another topic].

If a line has no slashes, the entire line is considered to be the phrase:

        This whole line is a topic.

By using `[]` brackets, the image for the topic enclosed will be randomly chosen. To have the first image from Bing
chosen instead, use `{}` instead.

        Good for {proper nouns} but not [improper nouns].
 
## Audio Recording
The audio recording is a .wav reading of the annotated transcript. :/ currently if Gentle fails to align the transcript 
and audio recording then the entire program will fail.

## Running the program
To run the program use the following command:
    
        python auto_vid_maker.py transcript_path audio_path video_path

Use the `-h` flag for more help. 
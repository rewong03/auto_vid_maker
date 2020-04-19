import os
import random
import subprocess
import shutil
import textwrap
from typing import Dict
from PIL import Image, ImageFont, ImageDraw
from google_images_download import google_images_download


def pull_image(keywords: str, image_dir, mode: str = "random") -> str:
    """Pulls images with a certain keyword.

    Parameters:
    keywords (str): Phrase to search for.
    image_dir (str): Directory to store downloaded images.
    mode (str): Either "random" or "relevant". "random" chooses a random image while
    relevant chooses the first search result.

    Returns:
    new_path (str): Path to downloaded image.
    """
    image_dir = os.path.join(image_dir, keywords)

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    limit = 50 if mode == "random" else 1
    cmd: str = f"python Bulk-Bing-Image-downloader/bbid.py -s \"{keywords}\" -o \"{image_dir}\" --limit {limit}"
    subprocess.call(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    path = os.path.join(image_dir, os.listdir(image_dir)[random.randint(0, len(os.listdir(image_dir)) - 1)])
    new_path: str = os.path.join(os.path.dirname(os.path.dirname(path)), os.path.basename(path))
    os.rename(path, new_path)
    shutil.rmtree(os.path.dirname(path))
    path = new_path
    new_path: str = os.path.join(os.path.dirname(image_dir), keywords + ".jpg")
    os.rename(path, new_path)

    return new_path


def draw_frame(image_path: str, phrase: str, image_dir: str, image_name: str) -> str:
    """Takes an image and places a phrase underneath it on a black background.

    Parameters:
    image_path (str): Image to use.
    phrase (str): Phrase to write underneath image.
    image_name (str): Name to give final image.
    image_dir (str): Location to save final image.

    Returns:
    (str): Path to final image.
    """
    background = Image.new('RGB', (800, 600), (0, 0, 0))

    image = Image.open(image_path)
    width, height = image.size

    # Need to find a better way to resize
    if width > 800 and height > 450:
        resize_factor = min([800 / width, 450 / height])
        print(resize_factor)
        width = round(width * resize_factor)
        height = round(height * resize_factor)
        image = image.resize((width, height))
    elif width > 800:
        resize_factor = 800 / width
        width = round(width * resize_factor)
        height = round(height * resize_factor)
        image = image.resize((width, height))
    elif height > 500:
        resize_factor = 500 / height
        width = round(width * resize_factor)
        height = round(height * resize_factor)
        image = image.resize((width, height))
    # Could use better line wrapping logic
    background.paste(image, (round((800 - width) / 2), round((450 - height) / 2)))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("Arial.ttf", 24)
    phrase: str = "\n".join(textwrap.wrap(phrase, width=60))
    phrase_pix_size: int = draw.textsize(phrase, font=font)[0]
    draw.text((round((800 - phrase_pix_size) / 2), 475), phrase, (255, 255, 255), font=font)
    background.save(os.path.join(image_dir, image_name))

    return os.path.join(image_dir, image_name)



if __name__ == "__main__":
    pass
    # import uuid
    # path = str(uuid.uuid4())
    # os.mkdir(path)
    # print(pull_image("ryan wong uchicago", path, mode="random"))

    #draw_frame("big_images.jpg", "Here is a very long phrase. It is intentionally very long in the hopes of forcing text wrap to work so that I can debug errors", ".", "my_test1.jpg")
import os
import random
import shutil
from typing import Dict
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
    downloader = google_images_download.googleimagesdownload()

    if mode == "relevant":
        args: Dict = {"keywords": keywords, "limit": 1, "output_directory": image_dir,
                      "no_directory": True}
        path: str = downloader.download(args)[0][keywords][0]
        print(path)
        new_path: str = os.path.join(os.path.dirname(path), keywords + ".jpg")
        print(new_path)
        os.rename(path, new_path)

        return new_path
    else:
        # Currently this method downloads all images before choosing which is slow but there is no gurantee
        # that if we randomly chose a link it would work.
        args: Dict = {"keywords": keywords, "limit": 50, "output_directory": image_dir,
                      "image_directory": keywords}
        path: str = downloader.download(args)[0][keywords][random.randint(0, 49)]
        new_path: str = os.path.join(os.path.dirname(os.path.dirname(path)), os.path.basename(path))
        os.rename(path, new_path)
        shutil.rmtree(os.path.dirname(path))
        path = new_path
        new_path: str = os.path.join(os.path.dirname(new_path), keywords + ".jpg")
        os.rename(path, new_path)

        return new_path


if __name__ == "__main__":
    import uuid
    path = str(uuid.uuid4())
    os.mkdir(path)
    print(pull_image("ryan wong uchicago", path, mode="random"))
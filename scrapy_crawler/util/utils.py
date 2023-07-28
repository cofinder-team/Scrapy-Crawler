from io import BytesIO

import requests


def save_image_from_url(image_url):
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()

    return BytesIO(response.content)

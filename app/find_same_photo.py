import requests
from PIL import Image
from io import BytesIO
from imagehash import phash

def fetch_image_hash(url: str):
    """
    Загружает изображение по URL и вычисляет его perceptual hash.

    :param url: URL изображения.
    :return: Хэш изображения или None в случае ошибки.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return phash(image)
    except Exception as e:
        print(f"Ошибка при обработке URL {url}: {e}")
        return None

def get_unique_images(urls: list[str], threshold: int = 5) -> list[str]:
    """
    Определяет уникальные изображения из списка URL на основе perceptual hashing.

    :param urls: Список URL изображений.
    :param threshold: Пороговое значение для разницы хэшей (по умолчанию 5).
    :return: Список URL уникальных изображений.
    """
    unique_hashes = []
    unique_urls = []

    for url in urls:
        image_hash = fetch_image_hash(url)
        if image_hash is None:
            continue

        # Проверяем, существует ли похожий хэш
        if not any(abs(image_hash - existing_hash) <= threshold for existing_hash in unique_hashes):
            unique_hashes.append(image_hash)
            unique_urls.append(url)

    return unique_urls

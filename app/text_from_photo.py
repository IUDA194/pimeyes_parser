import requests
import json
from googletrans import Translator

def upload_image(file_path):
    url = 'https://api.theyseeyourphotos.com/deductions'

    with open(file_path, 'rb') as image_file:
        files = {
            'file': ('blob', image_file, 'image/jpeg')
        }

        response = requests.post(url, files=files)

    print(response)

    if response.status_code == 200:
        print("Upload successful!")
        return response.json()
    else:
        print(f"Failed to upload. Status code: {response.status_code}")
        return response.text

def translate(data):
    # Инициализация переводчика
    print(data.get("data"))
    translator = Translator()

    # Перевод и форматирование
    translated_text = []
    for key, value in data['data'].items():
        key_rus = translator.translate(key, src='en', dest='ru').text
        value_rus = translator.translate(value, src='en', dest='ru').text
        translated_text.append(f"{key_rus}: {value_rus}")

    # Форматирование текста
    formatted_text = "\n".join(translated_text)

    # Вывод результата
    return formatted_text

def get_ansver(path):
    return translate(upload_image(path))

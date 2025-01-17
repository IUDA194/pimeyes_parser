# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем переменные среды
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем систему и устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 libxss1 libasound2 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxi6 libxtst6 libxrandr2 libatk-bridge2.0-0 libgbm-dev \
    fonts-liberation xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y \
    && rm google-chrome-stable_current_amd64.deb

# Устанавливаем ChromeDriver
ARG CHROMEDRIVER_VERSION=114.0.5735.90  # Укажите необходимую версию
RUN wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . /app

# Указываем команду для запуска приложения
CMD ["python", "main.py"]

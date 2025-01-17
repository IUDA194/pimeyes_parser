import re

import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

def extract_code(text):
    # Используем регулярное выражение для поиска 6-значного кода
    match = re.search(r'\b\d{6}\b', text)
    if match:
        return match.group(0)
    return None

# Функция для декодирования заголовков
def decode_header_value(header_value):
    decoded_parts = decode_header(header_value)
    return ''.join(
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded_parts
    )

# Подключение к серверу IMAP
def get_last_email(username, password, imap_server="imap.rambler.ru"):
    try:
        # Подключаемся к серверу
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        
        # Выбираем почтовый ящик
        mail.select("inbox")
        
        # Получаем последнюю почту (номер сообщения)
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        if not mail_ids:
            print("Нет сообщений.")
            return
        
        latest_email_id = mail_ids[-1]
        
        # Получаем содержимое письма
        status, data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]
        
        # Обработка письма
        msg = email.message_from_bytes(raw_email)
        subject = decode_header_value(msg["Subject"])
        from_ = decode_header_value(msg.get("From"))
        date_str = msg.get("Date")
        
        # Парсинг времени из заголовка
        email_date = datetime.strptime(date_str[:-6], "%a, %d %b %Y %H:%M:%S")
        current_time = datetime.utcnow()
        
        # Проверка, было ли доставлено в последнюю минуту
        time_difference = current_time - email_date
        delivered_recently = time_difference < timedelta(minutes=2)
        
        print(f"Тема: {subject}")
        print(f"От кого: {from_}")
        print(f"Время получения: {email_date}")
        print(f"Доставлено в последнюю минуту: {'Да' if delivered_recently else 'Нет'}")
        
        body = None
        
        # Если письмо содержит текст
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    print(f"Содержание:\n{body}")
                    break
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                body = msg.get_payload(decode=True).decode()
                print(f"Содержание:\n{body}")
        
        return {"body" : body, f"delivered_recently" : delivered_recently}
        
        # Закрываем соединение
        mail.logout()
    except Exception as e:
        print(f"Ошибка: {e}")
        
#print("Code is: ", extract_code(get_last_email(username, password).get("body")))
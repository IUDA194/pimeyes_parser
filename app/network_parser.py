import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_data_from_network(url : str) -> json:
    # Настройка опций Chrome для перехвата сетевых логов
    print("Подключение к ноде для парсинга результатов")
    test = False
    
    driver = None
    
    if test:
        chrome_options = Options()
        chrome_options.add_argument(
            "--headless"
        )
        driver = webdriver.Chrome(options=chrome_options)
    else:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")

        print(os.getenv("SELENIUM_URL"))

        driver = WebDriver(
            command_executor=f"{os.getenv("SELENIUM_URL")}",
            options=chrome_options
        )
        
    print("Подключение к ноде для парсинга результатов")

    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver.get(url)

    # Ожидание полной загрузки страницы
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".results-row"))
    )


    # Получение сетевых логов
    logs = driver.get_log("performance")

    # Фильтрация запросов к "https://jsc5.pimeyes.com/get_results"
    for log in logs:
        message = json.loads(log["message"])  # Лог в формате JSON
        method = message["message"]["method"]
        
        # Если это запрос и URL совпадает
        if method == "Network.requestWillBeSent":
            request_url = message["message"]["params"]["request"]["url"]
            if "get_results" in request_url:
                print(f"Запрос отправлен: {request_url}")

        # Если это ответ и URL совпадает
        if method == "Network.responseReceived":
            response_url = message["message"]["params"]["response"]["url"]
            if "get_results" in response_url:
                print(f"Ответ получен с URL: {response_url}")
                try:
                    # Получаем тело ответа
                    response_body = driver.execute_cdp_cmd(
                        "Network.getResponseBody",
                        {"requestId": message["message"]["params"]["requestId"]}
                    )
                    if not "No resource with given identifier found" in str(response_body['body']):
                        return response_body['body']
                except Exception as e:
                    print(f"Ошибка при получении тела ответа: {e}")
    driver.quit()
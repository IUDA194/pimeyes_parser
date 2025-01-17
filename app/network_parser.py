import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

def get_data_from_network(url : str) -> json:
    # Настройка опций Chrome для перехвата сетевых логов
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Включаем headless режим
    chrome_options.add_argument("--disable-dev-shm-usage")  # Использование /dev/shm
    chrome_options.add_argument("--no-sandbox")  # Отключение sandbox
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU
    chrome_options.add_argument("--remote-debugging-port=9222")  # Установка порта для отладки
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


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

print(get_data_from_network('https://pimeyes.com/en/results/xgy_241224k8xgz58undjvmjefd401a69?query=c0e6e7c7e7c6c30084dec3c35f67c3c1'))
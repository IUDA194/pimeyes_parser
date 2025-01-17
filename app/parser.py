import os
import pickle

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from app.network_parser import get_data_from_network
from app.get_email_code import extract_code, get_last_email

import time

url = "https://pimeyes.com/en"
cookies_file = "cookies/cookies.pkl"  # File to save cookies


def save_cookies(driver, file_path):
    with open(file_path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

def allow_cookies(driver):
    try:
        cookies_button = WebDriverWait(driver, 1.5).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                )
            )
        )
        cookies_button.click()
    except:
        print("Ошибка при принятии кукис")

def enter_verification_code(driver):
    try:
        time.sleep(1)
        # Получаем код для валидации class="verify-btn" delivered_recently
        result = get_last_email(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
        
        code = None
        
        if result.get("delivered_recently"):
            code = extract_code(result.get("body"))
        else:
            print("Ожидание подтверждения через почту")
            print(result)
            time.sleep(120)
            result = get_last_email(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
            if result:
                code = extract_code(result.get("body"))
            else:
                print("Ошибка при получении подтверждения через почту")
        
        # Убедимся, что код имеет длину 6 символов
        print(code)
        if code and len(code) != 6:
            raise ValueError("Код валидации должен быть длиной 6 символов.")

        # Найти все input-поля внутри div с классом "digits"
        inputs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.digits input[type='tel']"))
        )
        
        # Вводим каждую цифру кода в соответствующее поле
        for i, digit in enumerate(code):
            inputs[i].send_keys(digit)

        print("Код успешно введён.")
        
        # Найти кнопку верификации
        verify_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.verify-btn"))
        )
        
        # Принудительный клик на кнопку
        driver.execute_script("arguments[0].click();", verify_button)
        print("Принудительный клик выполнен.")
        
    except Exception as e:
        print(f"Ошибка при вводе кода: {e}")

def login(driver):
    try:
        auth_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.auth"))
        )
        auth_button.click()
        
        email_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".login-frm > div:nth-child(2) > input:nth-child(2)")
            )
        )
        email_field.send_keys(os.getenv("P_USERNAME"))

        password_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        password_field.send_keys(os.getenv("P_PASSWORD"))

        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-btn"))
        )
        login_button.click()
        
        try:
            # Проверка на наличие поля "Email Verification"
            email_verification_field = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//h2[text()='Email Verification']"))
            )
            if email_verification_field:
                print("Поле 'Email Verification' найдено.")
                # Нажимаем кнопку с классом 'resend-btn'
                resend_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.resend-btn"))
                )
                resend_button.click()
                print("Кнопка 'Resend' нажата.")
                enter_verification_code(driver=driver)
                
        except Exception as e:
            print(f"Ошибка: {e}")

        # Wait until logged in (e.g., by checking for an element visible after login)
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'My Subscription')]")
            )
        )

        # Save cookies after login
        save_cookies(driver, cookies_file)
        
    except Exception as e:
        print(e)
        print("skip auth_button click")

def validate_auth(driver):
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.auth"))
    )
    login_button.click()

    try:
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'My Subscription')]")
            )
        )
    except:
        login(driver=driver)

def go_to_main_menu(driver):
    try:
        menu_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#sidebar-navigation > div > div > div.logo-and-search > a",
                )
            )
        )
        menu_button.click()
    except:
        pass

def upload_photo(driver, path):
    print("Waiting for the upload button to be clickable...")
    upload_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="hero-section"]/div/div[1]/div/div/div[1]/button[2]')
        )
    )
    print("Upload button found. Clicking the upload button...")
    upload_button.click()

    print("Waiting for the file input field to be present...")
    file_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=file]"))
    )
    print(f"File input field found. Sending file path: {path}")
    file_input.send_keys(path)
    
    time.sleep(5)
    #driver.save_screenshot('screenshot.png')

    print("Waiting for required input fields to be present...")
    inputs = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//input[@required]"))
    )
    print(f"Found {len(inputs)} required input fields. Clicking them...")
    for input_element in inputs:
        input_element.click()


    print("Waiting for the start button to be present...")
    start_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//button[span[contains(text(), "Start Search")]]')
        )
    )
    print("Start button found. Clicking the start button...")
    start_button.click()
    print("Photo upload and search process initiated.")

def get_results(driver):
    try:
        results = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".results-row"))
        )

        current_url = driver.current_url
        print("link:", current_url)
        return get_data_from_network(url=current_url)
    except Exception as e: 
        print(e)
        return None

def find_face(path, url="https://pimeyes.com/en"):
    #return get_data_from_network("https://pimeyes.com/en/results/xgy_241224k8xgz58undjvmjefd401a69?query=c0e6e7c7e7c6c30084dec3c35f67c3c1")
    
    test = False
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

        driver = WebDriver(
            command_executor=f"{os.getenv("SELENIUM_URL")}",
            options=chrome_options
        )

    try:
        driver.get(url)

        if os.path.exists(cookies_file):
            load_cookies(driver, cookies_file)
            driver.refresh() 

            allow_cookies(driver=driver)

            print("start auth validation")

            validate_auth(driver)

        else:
            allow_cookies(driver=driver)
            login(driver=driver)

        go_to_main_menu(driver)

        print("wait")

        upload_photo(driver=driver, path=path)

        print("фото загруженно, жду результатов")

        image_urls = get_results(driver)
        
        print(f"результаты полученны, ссылка: {image_urls}")
        
        return image_urls

    except Exception as e:
        print(f"An exception occurred: {e}")

    finally:
        driver.quit()

import time
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

BASE_URL = "http://localhost:5000"


def _new_driver():
    # Chrome in headless mode so tests don’t pop a window
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def test_register_login_and_create_task_e2e():
    username = f"user_{uuid4().hex[:6]}"
    password = "Password123!"
    task_title = f"Task_{uuid4().hex[:6]}"

    driver = _new_driver()
    driver.implicitly_wait(5)

    try:
        # --- Register ---
        driver.get(f"{BASE_URL}/register")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "confirm").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "form").submit()

        # --- Login ---
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "form").submit()

        # --- Create task ---
        driver.get(f"{BASE_URL}/tasks/new")
        driver.find_element(By.NAME, "title").send_keys(task_title)
        driver.find_element(By.NAME, "description").send_keys("E2E description")
        driver.find_element(By.CSS_SELECTOR, "form").submit()

        time.sleep(1)  # let redirect render

        page_text = driver.page_source
        assert task_title in page_text

    finally:
        driver.quit()

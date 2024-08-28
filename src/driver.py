from selenium import webdriver

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from typing import Optional


import threading

# Modify WebDriverManager to use thread-local storage for WebDriver instances
class WebDriverManager:
    _instance = None
    _lock = threading.Lock()
    _thread_local = threading.local()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WebDriverManager, cls).__new__(cls)
        return cls._instance

    def get_driver(self, headless: Optional[bool] = True) -> WebDriver:
        if not hasattr(self._thread_local, 'driver') or not isinstance(self._thread_local.driver, WebDriver):
            options = Options()
            if headless:
                options.add_argument("--headless")
                options.add_argument("window-size=1920,1980")
                options.add_argument("start-maximized")
                options.add_argument("disable-infobars")
                options.add_argument("--disable-extensions")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
            self._thread_local.driver = webdriver.Chrome(options=options)
            # print(f"Initiated a new instance of Selenium WebDriver for thread {threading.get_ident()}")
        return self._thread_local.driver

    def close_driver(self):
        if hasattr(self._thread_local, 'driver') and isinstance(self._thread_local.driver, WebDriver):
            self._thread_local.driver.close()
            # print(f"Closed Selenium WebDriver instance for thread {threading.get_ident()}")
        self._thread_local.driver = None


def accept_cookies_conditions():
    driver = WebDriverManager().get_driver(headless=None)
    try:
        accept_button = WebDriverWait(driver=driver, timeout=5).until(EC.presence_of_element_located((By.XPATH,"//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 XWZjwc']")))
        accept_button.click()
    except (NoSuchElementException, TimeoutException):
        pass

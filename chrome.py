import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置 logging 配置
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger("DigitimesLogin")


class DigitimesLogin:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self._setup_driver()
        self.need_cookies = {
            "ProductDCMUse": "",
            "ProductDCMMemberID": "",
            "ProductDCMSession": "",
        }

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        logger.debug("Initialized Chrome driver with headless options.")
        return webdriver.Chrome(options=chrome_options)

    def _human_like_delay(self, min_seconds=1, max_seconds=3):
        """模擬人類輸入的延遲"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug("Human-like delay for %.2f seconds.", delay)
        time.sleep(delay)

    def login_and_get_cookies(self):
        try:
            # 打開網頁
            url = "https://www.digitimes.com.tw/mservice/login.asp?svc_type=DCM"
            self.driver.get(url)
            logger.info("Opened the login page: %s", url)

            # 等待 Email 輸入框加載
            logger.debug("Waiting for the email input field to load...")
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "checkid"))
            )
            logger.debug("Email input field loaded successfully.")

            # 獲取密碼輸入框
            try:
                password_input = self.driver.find_element(By.ID, "checkpwd")
                logger.debug("Password input field found.")
            except NoSuchElementException:
                logger.error("Password input field not found on the page.")
                return

            # 輸入帳號和密碼
            logger.info("Entering email and password...")
            email_input.send_keys(self.email)
            self._human_like_delay()  # 模擬人類輸入延遲
            logger.debug("Email entered.")

            password_input.send_keys(self.password)
            self._human_like_delay()  # 模擬人類輸入延遲
            logger.debug("Password entered.")

            # 點擊登入按鈕
            logger.info("Clicking the login button...")
            login_button = self.driver.find_element(By.CLASS_NAME, "my-button")
            ActionChains(self.driver).move_to_element(login_button).click().perform()
            logger.info("Login button clicked.")

            # 檢查是否有警示對話框
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                logger.warning("An alert appeared: %s", alert.text)
                alert.accept()
                logger.debug("Alert was accepted.")
            except TimeoutException:
                logger.info("No alert dialog appeared after clicking the login button.")

            # 等待驗證碼輸入框
            logger.debug("Waiting for verification code input fields to load...")
            input_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "verify-input"))
            )

            # 確認是否找到驗證碼輸入框
            if not input_elements:
                logger.error("Verification code input fields not found.")
                return

            # 輸入驗證碼
            verify_code = input("Please enter the verification code: ")
            for i, element in enumerate(input_elements):
                element.send_keys(verify_code[i])
                logger.debug("Entered digit %s of the verification code.", i + 1)
                self._human_like_delay(0.5, 1.5)  # 模擬較短的人類延遲

            # 點擊送出按鈕
            logger.info("Submitting the verification code...")
            submit_button = self.driver.find_element(By.ID, "submit")
            submit_button.click()
            logger.info("Verification code submitted.")

            # 等待頁面加載並獲取 Cookies
            logger.debug("Collecting cookies from the browser...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                if cookie["name"] in self.need_cookies:
                    self.need_cookies[cookie["name"]] = cookie["value"]
                    logger.debug(
                        "Collected cookie: %s = %s", cookie["name"], cookie["value"]
                    )

        except Exception as e:
            logger.exception("An unexpected error occurred: %s", str(e))
        finally:
            # 關閉瀏覽器
            self.driver.quit()
            logger.info("Browser session closed.")

        return self.need_cookies


# 使用範例
if __name__ == "__main__":
    email = "yahing6066@gmail.com"
    password = "pisXHwuZx7q8"
    login_handler = DigitimesLogin(email, password)
    cookies = login_handler.login_and_get_cookies()
    logger.info("Collected Cookies: %s", cookies)

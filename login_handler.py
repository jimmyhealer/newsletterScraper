import logging
import time
import random
from db import CredentialManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 設置 logging 配置
logger = logging.getLogger("DigitimesLogin")


class DigitimesLogin:
    def __init__(self, input_credentials_callback, input_verification_code_callback):
        self.input_credentials_callback = input_credentials_callback
        self.input_verification_code_callback = input_verification_code_callback
        self.driver = None
        self.need_cookies = {
            "ProductDCMSession": "",
            "ProductDCMMemberID": "",
            "ProductDCMUse": "",
        }

        self.credentials = CredentialManager()
        self.email, self.password = self.credentials.get_username_and_password()

        if not self.email and not self.password:
            logger.info("No credentials found in the database.")
            self.email, self.password = self.input_credentials_callback()
            self.credentials.set_username_and_password(self.email, self.password)

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
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug("Human-like delay for %.2f seconds.", delay)
        time.sleep(delay)

    def login_and_get_cookies(self):
        # Delay loading the driver until it is needed
        if not self.driver:
            self.driver = self._setup_driver()

        try:
            url = "https://www.digitimes.com.tw/mservice/login.asp?svc_type=DCM"
            self.driver.get(url)
            logger.info("Opened the login page: %s", url)

            success = False

            while not success:
                logger.debug("Waiting for the email input field to load...")
                email_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "checkid"))
                )
                logger.debug("Email input field loaded successfully.")

                try:
                    password_input = self.driver.find_element(By.ID, "checkpwd")
                    logger.debug("Password input field found.")
                except NoSuchElementException:
                    logger.error("Password input field not found on the page.")
                    return

                logger.info("Entering email and password...")
                email_input.send_keys(self.email)
                self._human_like_delay()
                logger.debug("Email entered.")

                password_input.send_keys(self.password)
                self._human_like_delay()
                logger.debug("Password entered.")

                logger.info("Clicking the login button...")
                login_button = self.driver.find_element(By.CLASS_NAME, "my-button")
                ActionChains(self.driver).move_to_element(
                    login_button
                ).click().perform()
                logger.debug("Login button clicked.")

                try:
                    WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert = self.driver.switch_to.alert
                    logger.warning("An alert appeared: %s", alert.text)
                    alert.accept()
                    logger.debug("Alert was accepted.")
                    self.email, self.password = self.input_credentials_callback(
                        again=True
                    )
                    self.credentials.set_username_and_password(
                        self.email, self.password
                    )
                except TimeoutException:
                    logger.info(
                        "No alert dialog appeared after clicking the login button."
                    )
                    success = True

            logger.debug("Waiting for verification code input fields to load...")
            input_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "verify-input"))
            )

            if not input_elements:
                logger.error("Verification code input fields not found.")
                return

            success = False

            while not success:
                verify_code = self.input_verification_code_callback()
                for i, element in enumerate(input_elements):
                    element.send_keys(verify_code[i])
                    logger.debug("Entered digit %s of the verification code.", i + 1)

                logger.info("Submitting the verification code...")
                submit_button = self.driver.find_element(By.ID, "submit")
                submit_button.click()
                logger.info("Verification code submitted.")

                try:
                    WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                    alert = self.driver.switch_to.alert
                    logger.error("An alert appeared: %s", alert.text)
                    logger.warning("You need to enter the correct verification code.")
                    alert.accept()
                    logger.debug("Alert was accepted.")
                except TimeoutException:
                    success = True
                    logger.info(
                        "No alert dialog appeared after clicking the verify button."
                    )

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

            return tuple(self.need_cookies.values())

        except Exception as e:
            logger.exception("An unexpected error occurred: %s", str(e))
            raise e
        finally:
            self.driver.quit()
            logger.info("Browser session closed.")

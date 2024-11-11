from db import get_username_and_password, set_username_and_password, get_product_dcm, set_product_dcm
from request import NewsletterRequest
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Flow():
    def __init__(self):
        self.username, self.password = get_username_and_password()
        self.session, self.member_id, self.use = get_product_dcm()
        self.request = NewsletterRequest()

    def run(self):
        ...
        # check has username and password

        # check session expired
        response = self.request.get_newsletter()
        regex = r"getContent\('(\d+)'\)"
        matches = re.findall(regex, response.text)

        if len(matches) == 0:
            logging.error("Session expired")

            # use chrome login again
            self.session, self.member_id, self.use = something()
            set_product_dcm(self.session, self.member_id, self.use)

        # get calander

        # get detail

        


if __name__ == "__main__":
    username, password = get_username_and_password()
    if not username or not password:
        username = input("請輸入帳號: ")
        password = input("請輸入密碼: ")
        set_username_and_password(username, password)

    print("帳號:", username)
    print("密碼:", password)

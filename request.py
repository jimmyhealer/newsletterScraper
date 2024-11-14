import requests
import requests.sessions


class NewsletterRequest:
    def __init__(self, session=None, member_id=None, use=None):
        self.session = requests.Session()
        self.cookies = {
            "ProductDCMSession": session,
            "ProductDCMMemberID": member_id,
            "ProductDCMUse": use,
        }

    def update_cookies(self, session, member_id, use):
        self.cookies.update({
            "ProductDCMSession": session,
            "ProductDCMMemberID": member_id,
            "ProductDCMUse": use,
        })

    def send(self, method, url, **kwargs):
        headers = {
            "cookie": "; ".join([f"{key}={value}" for key, value in self.cookies.items()]),
        }
        kwargs["headers"] = headers

        response = self.session.request(method, url, **kwargs)
        return response

    def get(self, url, **kwargs):
        return self.send("GET", url, **kwargs)

    def get_newsletter(self, date=None):
        url = f"https://www.digitimes.com.tw/mservice/dailynews_pc/?pub_date={date}"
        response = self.get(url)
        return response

    def get_newsletter_content(self, id):
        url = f"https://www.digitimes.com.tw/mservice/dailynews_pc/shwnws.asp?id={id}"
        response = self.get(url)
        return response
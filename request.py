import requests
import requests.sessions
import re
import json
from bs4 import BeautifulSoup


class NewsletterRequest:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = {
            # "ASPSESSIONIDSUCTTSBB": "FGMGMCBBMOADNIIKBJAABOHA",
            # "vid": "831a7baba3d88eab",
            # "ProductDCM": "Pwd=bd99e365821550a85178e266b4ebbd0e&ID=hungtse5436%40gmail%2Ecom",
            # "ASPSESSIONIDQUBQRRCA": "LHLCHOFANPIOHJHJCDBMDBKI",
            # "_gcl_au": "1.1.220894607.1731293257",
            # "_gid": "GA1.3.525023097.1731293257",
            # "_ga": "GA1.3.67006869.1731293257",
            # "_ga_04EJ418BDC": "GS1.3.1731293259.1.0.1731293259.0.0.0",
            # "_ga_C4DVYDG3EW": "GS1.1.1731293257.1.1.1731293261.56.0.0",
            "ProductDCMSession": "102833099",
            "ProductDCMMemberID": "FFB1C101",
            "ProductDCMUse": "yahing6066%40gmail%2Ecom",
            # "AWSALBTG": "TVHlCPXTzWKcOyUMXmvKP0M38SVbRwQuOpLDK+67mi+dD+pDPvksP0t7R3YrlBOwxSLKMLGs+FE/Kw3dduGrqe+Y6MV4+IK3l6M90+SoREdEnZ+c+fTfk/YquCBQUhspLqZk41/N3OIE0QxvQrkAN3q39kzh1EOTzJibKVgEwm340TUsMvA=",
            # "AWSALBTGCORS": "TVHlCPXTzWKcOyUMXmvKP0M38SVbRwQuOpLDK+67mi+dD+pDPvksP0t7R3YrlBOwxSLKMLGs+FE/Kw3dduGrqe+Y6MV4+IK3l6M90+SoREdEnZ+c+fTfk/YquCBQUhspLqZk41/N3OIE0QxvQrkAN3q39kzh1EOTzJibKVgEwm340TUsMvA=",
            # "AWSALB": "3af4VZktHLiWlAVmK48jDexIZTz2bEVHhzHpNthsFceu7xcnekCz5GU1Ep5vrlxbYQa0GveXxbJpfT/u7nRktwwzAnkbAODVCjJGyJ9lMaZT0rPswoxnZiUYVEw3",
            # "AWSALBCORS": "3af4VZktHLiWlAVmK48jDexIZTz2bEVHhzHpNthsFceu7xcnekCz5GU1Ep5vrlxbYQa0GveXxbJpfT/u7nRktwwzAnkbAODVCjJGyJ9lMaZT0rPswoxnZiUYVEw3",
        }

        self.headers = {
            "cookie": "; ".join([f"{key}={value}" for key, value in self.cookies.items()]),
        }

    def send(self, method, url, **kwargs):
        # 合併標頭，確保 `headers` 正確地傳遞
        if "headers" in kwargs:
            kwargs["headers"].update(self.headers)
        else:
            kwargs["headers"] = self.headers

        # 發送請求
        response = self.session.request(method, url, **kwargs)
        return response

    def get(self, url, **kwargs):
        return self.send("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.send("POST", url, **kwargs)
    
    def login(self):
        url = "https://www.digitimes.com.tw/mservice/login_act.asp?act=send"

        form_data = {
            "svc_type": "DCM",
            "checkid": "hungtse5436@gmail.com",
            "checkpwd": "e.3vm,6m04"
        }

        form_data = {
            "svc_type": "DCM",
            "checkid": "yahing6066@gmail.com",
            "checkpwd": "pisXHwuZx7q8",
        }

        response = self.post(url, data=form_data)
        return response
    
    def get_verification_code(self):
        url = "https://www.digitimes.com.tw/mservice/verify.asp"
        
        # 建立 form-data 資料
        form_data = {
            "uUID": "HUNGTSE5436@GMAIL.COM",
            "svc_type": "DCM",
            "mobile": "0928539636",
            "cate": "mobile"
        }

        form_data = {
            "uUID": "YAHING6066@GMAIL.COM",
            "svc_type": "DCM",
            "mobile": "0960518676",
            "cate": "mobile"
        }

        # 發送 POST 請求
        response = requests.post(url, data=form_data)
        
        return response
    
    def input_varification_code(self, code=""):
        url = "https://www.digitimes.com.tw/mservice/verify_act.asp"

        form_data = [
            ("uUID", "HUNGTSE5436@GMAIL.COM"),
            ("svc_type", "DCM"),
            ("mobile", "0928539636")
        ]

        form_data = [
            ("uUID", "YAHING6066@GMAIL.COM"),
            ("svc_type", "DCM"),
            ("mobile", "0960518676")
        ]

        # 將 code 字串逐個字元添加到 CheckCode
        for digit in code:
            form_data.append(("CheckCode", digit))

        response = self.post(url, data=form_data)
        if not "ProductDCMSession" in response.cookies:
            print("驗證碼輸入錯誤")
            for cookie in response.cookies:
                print(f"{cookie.name}: {cookie.value}")
        else:
            print(response.cookies["ProductDCMSession"])
        return response

    def get_newsletter(self):
        url = "https://www.digitimes.com.tw/mservice/dailynews_pc/"
        response = self.get(url)
        return response

    def get_newsletter_content(self, id):
        url = f"https://www.digitimes.com.tw/mservice/dailynews_pc/shwnws.asp?id={id}"
        response = self.get(url)
        return response

if __name__ == "__main__":
    request = NewsletterRequest()
    # response = request.login()
    # print(response.text)
    # response = request.get_verification_code()
    # code = input("請輸入驗證碼: ")
    # response = request.input_varification_code(code)
    # if len(response.text) < 600:
    #     print(response.text)

    # exit()
    response = request.get_newsletter()

    regex = r"getContent\('(\d+)'\)"
    matches = re.findall(regex, response.text)

    print(matches)

    for match in matches:
        response = request.get_newsletter_content(match)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取標題
        main_title = soup.find('div', class_='main-title').get_text(strip=True)
        # print("標題:", main_title)

        label = soup.find('labal', class_='labal').get_text(strip=True)
        # print("標籤:", label)

        # 提取作者
        author = soup.find('div', class_='author').get_text(strip=True)
        # print("作者:", author)

        # 提取內文
        content_div = soup.find('div', class_='content')
        content = content_div.get_text("\n", strip=True)
        # print("內文:", content)

        # 提取圖片
        images = soup.find_all('img', class_='photo')
        image_urls = [img['src'] for img in images]
        # print("圖片 URLs:", image_urls)

        for image_url in image_urls:
            response = request.get(image_url)
            with open(image_url.split("/")[-1], "wb") as f:
                f.write(response.content)

            image_url = image_url.split("/")[-1]

        data = {
            "標題": main_title,
            "標籤": label,
            "作者": author,
            "內文": content,
            "圖片 URLs": image_urls
        }

        with open(f"{main_title}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # break
import concurrent.futures
from db import CredentialManager
from request import NewsletterRequest
from bs4 import BeautifulSoup
from utils import closest_weekday_before_today
import re
from io import BytesIO
from rich.progress import Progress


class ScraperService:
    def __init__(self):
        self.credential_manager = CredentialManager()
        self.session, self.member_id, self.use = (
            self.credential_manager.get_product_dcm()
        )
        self.request = NewsletterRequest(self.session, self.member_id, self.use)

    def update_cookies(self, session, member_id, use):
        self.session, self.member_id, self.use = session, member_id, use
        self.credential_manager.set_product_dcm(session, member_id, use)
        self.request.update_cookies(session, member_id, use)

    def _parse_newsletter(self, response, date=None):
        regex = r"getContent\('(\d+)'\)"
        matches = re.findall(regex, response.text)
        matches = [(match, date) for match in matches]
        return matches

    def _parse_newsletter_content(self, response, date):
        soup = BeautifulSoup(response.text, "html.parser")
        main_title = soup.find("div", class_="main-title").get_text(strip=True)
        label = soup.find("labal", class_="labal").get_text(strip=True)
        author = soup.find("div", class_="author").get_text(strip=True)
        content_div = soup.find("div", class_="content")
        for strong_tag in content_div.find_all("strong"):
            strong_text = strong_tag.get_text(strip=True)
            formatted_text = f"**{strong_text}**"
            strong_tag.replace_with(formatted_text)

        content = content_div.get_text("\n\n", strip=True)
        images = soup.find_all("img", class_="photo")
        image_urls = [img["src"] for img in images]

        images = []

        for image_url in image_urls:
            response = self.request.get(image_url)
            response.raise_for_status()
            image = BytesIO(response.content)
            images.append(image)

        data = {
            "title": main_title,
            "label": label,
            "author": author,
            "content": content,
            "images": images,
            "date": date,
        }

        return data

    def check_session_expired(self):
        if not self.session and not self.member_id and not self.use:
            return True

        today = closest_weekday_before_today()
        response, _ = self.request.get_newsletter(today)
        matches = self._parse_newsletter(response)
        return len(matches) == 0

    def get_newsletter_ids(self, need_dates=None):
        matches = []
        with Progress() as progress:
            task = progress.add_task(
                "[cyan] 正在抓取新聞 ID ...", total=len(need_dates)
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_date = {
                    executor.submit(self.request.get_newsletter, date): date
                    for date in need_dates
                }

                for future in concurrent.futures.as_completed(future_to_date):
                    try:
                        response, date = future.result()
                        matches.extend(self._parse_newsletter(response, date))
                    except Exception as e:
                        print(
                            f"Error fetching newsletter id for {future_to_date[future]}: {e}"
                        )
                    finally:
                        progress.update(task, advance=1)

            return matches

    def get_newsletter_content(self, ids):
        datas = []
        with Progress() as progress:
            task = progress.add_task("[cyan] 正在抓取新聞內容...", total=len(ids))
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_id = {
                    executor.submit(self.request.get_newsletter_content, id[0], id[1]): id
                    for id in ids
                }

                for future in concurrent.futures.as_completed(future_to_id):
                    try:
                        response, date = future.result()
                        datas.append(self._parse_newsletter_content(response, date))
                    except Exception as e:
                        print(
                            f"Error fetching newsletter content for {future_to_id[future]}: {e}"
                        )
                    finally:
                        progress.update(task, advance=1)

        return datas

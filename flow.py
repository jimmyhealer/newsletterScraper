from utils import closest_weekday_before_today, working_days_between
import logging
from login_handler import DigitimesLogin
from service import ScraperService
from to_word import data_to_word
from rich.console import Console
from rich.prompt import Prompt
import calendar
from datetime import datetime

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="digitimes.log",
)

console = Console()


class Flow:
    def __init__(self):
        self.login_handler = DigitimesLogin(
            self.login_without_credentials, self.request_verification_code
        )
        self.scraping_service = ScraperService()
        self.loading_status = None

    def loading_stop(self):
        if self.loading_status:
            self.loading_status.stop()
        
    def loading_start(self):
        if self.loading_status:
            self.loading_status.start()

    def login_without_credentials(self, again=False):
        # 使用 rich 的 Prompt 來輸入帳號和密碼
        self.loading_stop()
        if again:
            console.print("[red]帳號或密碼錯誤，請重新輸入[/red]")
        self.username = Prompt.ask("[bold blue]請輸入帳號[/bold blue]")
        self.password = Prompt.ask("[bold blue]請輸入密碼[/bold blue]", password=True)
        self.loading_start()

        return self.username, self.password

    def request_verification_code(self):
        # 使用 rich 的 Prompt 來輸入驗證碼
        self.loading_stop()
        code = Prompt.ask("[bold blue]請輸入驗證碼[/bold blue]")
        self.loading_start()
        return code

    def input_calendar_date(self):
        # 顯示當月日曆
        today = datetime.today()
        year = today.year
        month = today.month
        cal = calendar.TextCalendar()

        console.print(f"[green]今日可抓取: {closest_weekday_before_today()}[/green]")
        console.print("[bold yellow]當月日曆:[/bold yellow]")
        console.print(cal.formatmonth(year, month))

        # 用戶輸入日期
        success = False
        while not success:
            try:
                date = Prompt.ask(
                    "[bold blue]請輸入從哪天開始抓取 (YYYY/MM/DD)[/bold blue]"
                )
                working_days = working_days_between(date)

                if working_days < 0:
                    console.print("[red]日期不能大於今天[/red]")
                    continue

                if working_days > 10:
                    console.print(
                        f"[red]總共 {working_days} 天，會有較長的等待時間[/red]"
                    )
                    response = Prompt.ask("[bold blue]是否繼續？(y/n)[/bold blue]")
                    if response.lower() != "y":
                        continue

                success = True
            except ValueError:
                console.print("[red]日期格式錯誤，請重新輸入[/red]")
                continue

        console.print(f"[green]總共需要抓取 {working_days} 天[/green]")
        return date

    def run(self):
        console.rule("[bold yellow]歡迎使用數位電子報抓取工具[/bold yellow]")
        # 檢查 session 是否過期
        if self.scraping_service.check_session_expired():
            logging.warning("Session expired, logging in again...")
            console.print("[bold yellow] 登入 [/bold yellow]")

            # 使用 rich 的 Spinner 來顯示加載動畫
            with console.status(
                "[bold yellow]正在重新登入...[/bold yellow]", spinner="dots"
            ) as status:
                self.loading_status = status
                # 使用瀏覽器重新登錄
                self.session, self.member_id, self.use = (
                    self.login_handler.login_and_get_cookies()
                )

            # 登錄成功後顯示提示
            console.print("[green]登入成功！[/green]")

            # Debug 訊息記錄
            logging.debug(
                f"session: {self.session}, member_id: {self.member_id}, use: {self.use}"
            )
            self.scraping_service.update_cookies(self.session, self.member_id, self.use)

        # 獲取日曆
        date_str = self.input_calendar_date()
        matches = self.scraping_service.get_newsletter_ids(date_str)

        # 使用 rich 的進度條顯示抓取進度
        datas = self.scraping_service.get_newsletter_content(matches)

        # 將抓取到的數據寫入 Word 文件
        data_to_word(datas)
        console.print("[bold green]抓取完成並成功匯出 Word 文件[/bold green]")


if __name__ == "__main__":
    flow = Flow()
    flow.run()

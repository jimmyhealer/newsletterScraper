from utils import closest_weekday_before_today, working_days_between
import logging
from login_handler import DigitimesLogin
from service import ScraperService
from to_word import data_to_word
from utils import add_working_day
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
        self.loading_status = None
        self.login_handler = DigitimesLogin(
            self.login_without_credentials, self.request_verification_code
        )
        self.scraping_service = ScraperService()

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
        self.password = Prompt.ask("[bold blue]請輸入密碼[/bold blue]")
        self.loading_start()

        return self.username, self.password

    def request_verification_code(self):
        # 使用 rich 的 Prompt 來輸入驗證碼
        self.loading_stop()
        code = Prompt.ask("[bold blue]請輸入驗證碼[/bold blue]")
        self.loading_start()
        return code

    def input_date_range(self):
        success = False
        while not success:
            try:
                start_date = Prompt.ask(
                    "[bold blue]請輸入開始日期 (YYYY/MM/DD)[/bold blue]"
                )
                end_date = Prompt.ask(
                    "[bold blue]請輸入結束日期 (YYYY/MM/DD)[/bold blue]"
                )

                working_days = working_days_between(start_date, end_date)
                if working_days < 0:
                    console.print("[red]結束日期不能小於開始日期[/red]")
                    continue

                console.print(f"[green]總共需要抓取 {working_days} 天[/green]")
                success = True
            except ValueError:
                console.print("[red]日期格式錯誤，請重新輸入[/red]")
                continue

        return add_working_day(start_date, end_date)

    def input_single_date(self):
        success = False
        while not success:
            try:
                now_str = closest_weekday_before_today()
                date = Prompt.ask(
                    "[bold blue]請輸入要抓取的日期 (YYYY/MM/DD)[/bold blue]",
                    default=now_str,
                )
                now = datetime.strptime(now_str, "%Y/%m/%d")
                input_date = datetime.strptime(date, "%Y/%m/%d")

                if input_date > now:
                    console.print("[red]日期不能大於今天[/red]")
                    continue

                success = True
            except ValueError:
                console.print("[red]日期格式錯誤，請重新輸入[/red]")
                continue

        return [date]

    def input_calendar_date(self):
        # 顯示當月日曆
        today = datetime.today()
        year = today.year
        month = today.month
        cal = calendar.TextCalendar()

        console.print(f"[green]今日可抓取: {closest_weekday_before_today()}[/green]")
        console.print("[bold yellow]當月日曆:[/bold yellow]")
        console.print(cal.formatmonth(year, month))

        date_option = Prompt.ask(
            "[bold blue]選擇日期輸入模式: 1. 單一日期 2. 開始和結束日期 (輸入 1 或 2)[/bold blue]",
            choices=["1", "2"],
            default="1",
        )

        # 用戶輸入日期
        if date_option == "2":
            return self.input_date_range()
        else:
            return self.input_single_date()

    def run(self):
        console.rule("[bold yellow]歡迎使用數位電子報抓取工具[/bold yellow]")
        # 檢查 session 是否過期
        while self.scraping_service.check_session_expired():
            logging.warning("Session expired, logging in again...")
            console.print("[bold yellow] 登入 [/bold yellow]")

            # 使用 rich 的 Spinner 來顯示加載動畫
            with console.status(
                "[bold yellow]正在重新登入...[/bold yellow]", spinner="dots"
            ) as status:
                self.loading_status = status
                # 使用瀏覽器重新登錄
                session, member_id, use = (
                    self.login_handler.login_and_get_cookies()
                )

            # 登錄成功後顯示提示
            console.print("[green]登入成功！[/green]")

            # Debug 訊息記錄
            logging.debug(
                f"session: {session}, member_id: {member_id}, use: {use}"
            )
            self.scraping_service.update_cookies(session, member_id, use)

        # 獲取日曆
        dates = self.input_calendar_date()
        matches = self.scraping_service.get_newsletter_ids(dates)
        console.print(f"[green]總共抓取到 {len(matches)} 篇新聞[/green]")

        # 使用 rich 的進度條顯示抓取進度
        datas = self.scraping_service.get_newsletter_content(matches)

        # 將抓取到的數據寫入 Word 文件
        data_to_word(datas)
        console.print("[bold green]抓取完成並成功匯出 Word 文件[/bold green]")


if __name__ == "__main__":
    flow = Flow()
    flow.run()

import argparse
import os
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


REQUIRED_CONFIG = ("url", "username", "password")


def env_or_default(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="O2O 商城下单流程 Selenium 自动化脚本")
    parser.add_argument("--url", default=env_or_default("O2O_URL"), help="O2O 商城测试环境地址")
    parser.add_argument("--username", default=env_or_default("O2O_USERNAME"), help="登录账号")
    parser.add_argument("--password", default=env_or_default("O2O_PASSWORD"), help="登录密码")
    parser.add_argument("--keyword", default=env_or_default("O2O_KEYWORD", "坐垫"), help="搜索关键词")
    parser.add_argument("--timeout", type=int, default=int(env_or_default("O2O_TIMEOUT", "15")))
    parser.add_argument("--headless", action="store_true", help="使用无界面模式运行 Chrome")
    parser.add_argument(
        "--screenshot",
        default=env_or_default("O2O_SCREENSHOT", "o2o_error_screenshot.png"),
        help="失败时保存的截图路径",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    missing = [name for name in REQUIRED_CONFIG if not getattr(args, name)]
    if missing:
        names = ", ".join(f"O2O_{name.upper()}" for name in missing)
        raise ValueError(f"缺少必要配置：{names}。请通过环境变量或命令行参数提供。")


def create_driver(headless: bool) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1440,1000")
    return webdriver.Chrome(options=chrome_options)


class O2OMallFlow:
    def __init__(self, driver: webdriver.Chrome, timeout: int) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def click(self, by: str, value: str) -> None:
        self.wait.until(EC.element_to_be_clickable((by, value))).click()

    def input_text(self, by: str, value: str, text: str, clear: bool = True) -> None:
        element = self.wait.until(EC.visibility_of_element_located((by, value)))
        if clear:
            element.clear()
        element.send_keys(text)

    def run(self, url: str, username: str, password: str, keyword: str) -> None:
        self.driver.get(url)

        self.click(By.XPATH, "//a[normalize-space()='登录']")
        self.input_text(
            By.XPATH,
            "//input[@placeholder='请输入账号' or contains(@placeholder, '账号')]",
            username,
        )
        self.input_text(
            By.XPATH,
            "//input[@type='password' or contains(@placeholder, '密码')]",
            password,
            clear=False,
        )
        self.click(By.XPATH, "//button[normalize-space()='登录']")

        self.print_login_tip_if_present()
        self.search_keyword(keyword)
        self.open_second_goods()
        self.buy_now()
        self.select_second_address()
        self.submit_order()
        self.select_alipay()
        self.confirm_pay()
        self.open_my_order()
        self.print_first_paid_order()

    def print_login_tip_if_present(self) -> None:
        try:
            tip = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(text(), '账号不存在') or contains(text(), '密码错误')]",
                    )
                )
            )
            print(f"登录提示：{tip.text}")
        except TimeoutException:
            print("登录成功，未发现账号或密码错误提示")

    def search_keyword(self, keyword: str) -> None:
        self.input_text(
            By.XPATH,
            "/html/body/div/div[3]/div/div/div[2]/div/div[1]/div/input",
            keyword,
        )
        self.click(By.XPATH, "/html/body/div/div[3]/div/div/div[2]/div/div[1]/button")

    def open_second_goods(self) -> None:
        before_handles = set(self.driver.window_handles)
        self.click(By.XPATH, "/html/body/div/div[4]/div[2]/div/div[1]/div/div[2]/a/div[1]/img")

        try:
            self.wait.until(lambda driver: len(driver.window_handles) > len(before_handles))
            new_handles = [handle for handle in self.driver.window_handles if handle not in before_handles]
            self.driver.switch_to.window(new_handles[-1])
        except TimeoutException:
            self.driver.switch_to.window(self.driver.window_handles[-1])

        print(f"当前窗口数量：{len(self.driver.window_handles)}")
        print("已切换到商品详情页窗口")

    def buy_now(self) -> None:
        self.click(By.XPATH, "/html/body/div/div[4]/div/div[1]/div[2]/form/button[2]/span")

    def select_second_address(self) -> None:
        self.click(By.XPATH, "/html/body/div/div[4]/div/div/div[2]/div[2]/ul/li[2]/div[2]/span")

    def submit_order(self) -> None:
        self.click(By.XPATH, "/html/body/div/div[4]/div/div/div[2]/div[8]/div[3]/button/span")

    def select_alipay(self) -> None:
        self.click(By.XPATH, "/html/body/div/div[4]/div/div/div[2]/div[2]/ul/li[2]/div/img")

    def confirm_pay(self) -> None:
        self.click(By.XPATH, "//button[normalize-space()='确认支付' or contains(., '确认支付')]")

    def open_my_order(self) -> None:
        self.click(By.XPATH, "/html/body/div/div[3]/div/div[2]/div[1]/span[2]/span[1]")

    def print_first_paid_order(self) -> None:
        order = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div/div[3]/div/div[2]/div[2]/div[3]/div[1]/a/ul/li/div[2]")
            )
        )
        print("\n已支付订单信息：")
        print(order.text)


def main() -> int:
    args = build_parser().parse_args()
    screenshot_path = Path(args.screenshot)
    driver = None

    try:
        validate_args(args)
        driver = create_driver(args.headless)
        O2OMallFlow(driver, args.timeout).run(
            url=args.url,
            username=args.username,
            password=args.password,
            keyword=args.keyword,
        )
        return 0
    except Exception as exc:
        if driver is not None:
            try:
                driver.save_screenshot(str(screenshot_path))
                print(f"\n脚本执行出错，已保存截图：{screenshot_path.resolve()}")
            except Exception as screenshot_exc:
                print(f"\n脚本执行出错，截图保存失败：{screenshot_exc}")
        print(f"错误信息：{exc}")
        return 1
    finally:
        if driver is not None:
            time.sleep(2)
            driver.quit()


if __name__ == "__main__":
    sys.exit(main())

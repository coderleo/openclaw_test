"""
示例：在你的 Selenium 爬虫里集成验证码人机协作
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from client import CaptchaSolver


def main():
    driver = webdriver.Chrome()
    solver = CaptchaSolver(server_url="http://127.0.0.1:5555", timeout=120)

    driver.get("https://example.com/target-page")

    try:
        # 检测是否出现验证码（根据你实际的页面结构调整选择器）
        captcha = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha-image"))
        )
        print("检测到验证码，请求人工协助...")
        success = solver.solve(driver, captcha)
        if success:
            print("验证码已通过，继续爬取")
        else:
            print("验证码超时，可能需要刷新重试")

    except Exception:
        # 没有验证码，正常继续
        print("无验证码，正常爬取")

    # 继续你的爬虫逻辑...
    driver.quit()


if __name__ == "__main__":
    main()

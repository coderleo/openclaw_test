"""
爬虫端调用的客户端
在 Selenium 脚本里检测到验证码时调用
"""
import time
import requests
from selenium.webdriver.common.action_chains import ActionChains


class CaptchaSolver:
    def __init__(self, server_url="http://127.0.0.1:5555", timeout=120):
        """
        server_url: 验证码协作服务器地址
        timeout: 等待人工回复的超时时间（秒）
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout

    def solve(self, driver, captcha_element):
        """
        主流程：截图 → 提交 → 等待 → 点击
        
        driver: Selenium WebDriver 实例
        captcha_element: 验证码图片所在的 WebElement
        返回: True 成功点击, False 超时
        """
        # 1. 截图验证码区域
        screenshot = captcha_element.screenshot_as_png

        # 2. 提交到协作服务器
        resp = requests.post(
            f"{self.server_url}/submit",
            data=screenshot,
            headers={"Content-Type": "application/octet-stream"},
        )
        task_id = resp.json()["task_id"]
        print(f"[CaptchaSolver] 验证码已提交, task_id={task_id}, 等待人工处理...")

        # 3. 轮询等待结果
        start = time.time()
        while time.time() - start < self.timeout:
            resp = requests.get(f"{self.server_url}/poll/{task_id}")
            data = resp.json()
            if data["status"] == "solved":
                clicks = data["clicks"]
                print(f"[CaptchaSolver] 收到坐标: {clicks}")
                # 4. 自动点击
                for point in clicks:
                    ActionChains(driver).move_to_element_with_offset(
                        captcha_element, point["x"], point["y"]
                    ).click().perform()
                    time.sleep(0.3)
                print(f"[CaptchaSolver] 已完成 {len(clicks)} 次点击")
                return True
            time.sleep(2)  # 每2秒轮询一次

        print(f"[CaptchaSolver] 超时 ({self.timeout}s)，未收到人工回复")
        return False

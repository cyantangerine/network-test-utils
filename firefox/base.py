import time
import keyboard
import pyautogui
from selenium import webdriver
from conf import MAX_PAGES, URLS_TXT_PATH2, REFRESH_TIMES, REFRESH_ABORT


class FirefoxBaseOperator:
    def __init__(self, data_map_mixin):
        # self.res_file = None
        self.data_map_mixin = data_map_mixin
        self.data_map = []
        for i in range(MAX_PAGES):
            target = {
                "repeat_time": 0,
                "get_success": False
            }
            target.update(data_map_mixin)
            self.data_map.append(target)

        self.window_handles = []
        self.windows_urls = ["" for i in range(MAX_PAGES)]
        self.screenWidth, self.screenHeight = pyautogui.size()
        self.windowLeft = self.screenWidth * 0.1
        self.windowWidth, self.windowHeight = self.screenWidth * 0.5, self.screenHeight * 0.5
        service = webdriver.FirefoxService(executable_path="./geckodriver.exe")
        self.browser = webdriver.Firefox(service=service)
        self.browser.set_window_rect(self.windowLeft, 0, self.windowWidth, self.windowHeight)
        with open(URLS_TXT_PATH2, "r") as file:
            self.urls = file.readlines()

    def _clear_data_item(self, current):
        self.data_map[current] = {
            "repeat_time": 0,
            "get_success": False
        }
        self.data_map[current].update(self.data_map_mixin)

    def run(self, prepare_todo, function_todo, fail_todo):
        # self.res_file = res_file
        time_start_1 = time.time()
        print("准备中，请不要操作，准备完毕自动开始")
        if prepare_todo:
            prepare_todo()
        time.sleep(0.2)
        # 准备完毕
        # total_round = math.ceil(len(self.urls) / MAX_PAGES)
        progress_index = 0
        opened_index = 0
        current = 0
        while progress_index < len(self.urls):
            # 检查页面池
            handle = None
            while handle is None:
                # 检查是否有可切换的页面
                current = (current + 1) % MAX_PAGES
                check_handle = self.window_handles[current]
                self.switch_to_window(current)
                check_url = self.windows_urls[current]
                print("切换到：" + check_url)
                time.sleep(0.2)
                self.data_map[current]["repeat_time"] += 1
                if check_url != "" and 0 == self.data_map[current]["repeat_time"] % REFRESH_TIMES:
                    if REFRESH_ABORT + 1 == self.data_map[current]["repeat_time"] // REFRESH_TIMES:
                        # 超过手动刷新上限，放弃
                        handle = check_handle
                        progress_index += 1
                        print(f"进度：{progress_index}/{len(self.urls)}")
                        if fail_todo:
                            fail_todo(check_url, current)
                        self._clear_data_item(current)
                        break
                    # 超过次数仍未加载成功，手动等待
                    # open_url(check_url,check_handle)
                    print("等待次数超限(测试DOMC如果未出现DOMC请刷新)，按p继续")
                    keyboard.wait("p")
                if self.check_load_success():
                    if check_url != "":
                        if function_todo(check_url, current):
                            self._clear_data_item(current)
                            print(f"取数据成功，重复次数{self.data_map[current]['repeat_time']}")
                            progress_index += 1
                            print(f"进度：{progress_index}/{len(self.urls)}")
                        else:
                            self.data_map[current]["get_success"] = True
                            print(f"取数据存在变化，等待下一次，重复次数{self.data_map[current]['repeat_time']}")
                            continue
                    handle = check_handle
                    break
            if opened_index < len(self.urls):
                url = self.urls[opened_index].strip()
                self.windows_urls[current] = url
                self.open_url("https://" + url, handle)
                opened_index += 1
                time.sleep(1)
            elif self.windows_urls[current] != "":
                self.windows_urls[current] = ""
                self.open_url("about:blank", handle)
        time_end_1 = time.time()
        print("运行时间：" + str(time_end_1 - time_start_1) + "秒")

    def open_url(self, url, handle):
        self.browser.switch_to.window(handle)
        self.browser.execute_script("window.location=\"" + url + "\"")
        print(f"URL: {url}")

    def open_pages(self, network_analyze_point=None):
        for i in range(MAX_PAGES - 1):
            js = 'window.open("https://today.hit.edu.cn");'
            self.browser.execute_script(js)
            time.sleep(1)
            pyautogui.hotkey("ctrl", "shift", "e")
            time.sleep(0.5)
            if network_analyze_point:
                pyautogui.click(network_analyze_point.x, network_analyze_point.y)
                time.sleep(1)
        self.window_handles = self.browser.window_handles
        self.browser.switch_to.window(self.window_handles[0])

    def switch_to_window(self, index):
        self.browser.switch_to.window(self.window_handles[index])

    def check_load_success(self):
        # 页面加载完成
        # wait = WebDriverWait(browser, 1)
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # 判断页面是否完全加载
        if self.browser.execute_script("return document.readyState") == "complete":
            print("页面加载完成")
            return True
        else:
            print("页面加载未完成")
            return False

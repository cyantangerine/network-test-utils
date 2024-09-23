import time
import keyboard
import pyautogui
import pyperclip

from conf import RESULT_PATH
from util.hotkey import SystemHotkey
from .base import FirefoxBaseOperator


# SystemHotkey()


class FirefoxDomcOperator(FirefoxBaseOperator):
    def __init__(self):
        super().__init__({
            "last_domc": "0"
        })
        self.domc_point = self._get_mouse_position()
        self.result_list = []

    def _get_mouse_position(self):
        self.browser.get('https://today.hit.edu.cn')
        time.sleep(1)
        pyautogui.hotkey("ctrl", "shift", "e")
        while not self.check_load_success():
            time.sleep(0.5)
        pyautogui.hotkey("f5")
        while not self.check_load_success():
            time.sleep(0.5)
        print("将鼠标移动到DOMC上, 如果未出现，请刷新，按下p继续")
        keyboard.wait("p")
        p2 = pyautogui.position()
        print(p2)
        return p2

    def _get_data(self, url, index):
        last_data = self.data_map[index]["last_domc"]
        pyautogui.click(self.domc_point)
        SystemHotkey.copy_all()
        temp_all = pyperclip.paste()
        if "DOMContentLoaded" not in temp_all:
            return False
        content = temp_all
        content = content.replace(",", "")
        print("data: " + content.replace("\n", "").replace("\r", ""))
        index1_s = content.find("DOMContentLoaded:")
        index1_e = content.find("秒", index1_s)
        index1_e2 = content.find("钟", index1_s)
        if index1_s == -1 or (index1_e == -1 and index1_e2 == -1):
            return False
        index1_e = index1_e if index1_e != -1 else index1_e2
        content1 = content[index1_s + 17: index1_e].strip()
        if content1 == "0" or content1 == "0 毫":
            return False
        if content1.find("毫") != -1:
            content1 = content1.replace("毫", "")
            content1 = content1.strip()
            content1 = content1 + "ms"
        elif content1.find("分") != -1:
            content1 = content1.replace("分", "")
            content1 = content1.strip()
            content1 = content1 + "min"
        else:
            content1 = content1 + "s"
        if content1 == last_data:
            print(f"{url}, DOMContentLoaded: {content1}")
            self.result_list.append((url, content1))
            return True
        self.data_map[index]["last_domc"] = content1
        return False

    def run(self):
        self.result_list = []

        def prepare_todo():
            self.open_pages()

        def fail_todo(url, current):
            item = self.data_map[current]
            if item["get_success"]:  # 曾加载成功，但每次一直在增长（包括一次手动按p），可能是因为页面onShow会请求资源，导致每次都会增长，进而判定失败，这里直接使用最后一次的数值做处理。
                self.result_list.append((url, item["last_domc"]))
                return
            self.result_list.append((url, "超时"))
            # res_file.write(f"{url},超时,超时\n")

        try:
            super().run(prepare_todo, self._get_data, fail_todo)
        except KeyboardInterrupt:
            pass
        print("正在保存记录...")
        self.result_list = sorted(self.result_list, key=lambda t: t[0])
        result_name = "firefox_domc_result.csv"
        res_file = open(RESULT_PATH + result_name, "w")
        res_file.write("url, domctime\n")
        for p in self.result_list:
            res_file.write(f"{p[0]}, {p[1]}\n")
        res_file.close()
        # 关闭浏览器
        # browser.quit()

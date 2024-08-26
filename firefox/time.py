import time

import keyboard
import pyautogui
import pyperclip

from conf import RESULT_PATH
from util.hotkey import SystemHotkey
from .base import FirefoxBaseOperator


# SystemHotkey()

class FirefoxTimeOperator(FirefoxBaseOperator):
    def __init__(self):
        super().__init__({
            "last_size": "0",
            "last_time": "0"
        })
        self.network_analyze_point, self.non_block_time_point = self._get_mouse_position()
        self.result_list = []

    def _get_mouse_position(self):
        self.browser.get('https://today.hit.edu.cn')
        time.sleep(1)
        pyautogui.hotkey("ctrl", "shift", "e")
        print("将鼠标移动到启用性能分析（左下角秒表）上，按下p继续")
        time.sleep(1)
        keyboard.wait("p")
        p1 = pyautogui.position()
        # pyautogui.click(windowLeft + 10, windowHeight - 10)
        pyautogui.click(p1.x, p1.y)
        while not self.check_load_success():
            time.sleep(0.5)
        print("将鼠标移动到无阻塞时间上，按下p继续")
        keyboard.wait("p")
        p2 = pyautogui.position()
        print(p1, p2)
        return [p1, p2]

    def _get_data(self, url, index):
        last_data = self.data_map[index]["last_size"]
        # content1 = "0"
        # content2 = "0"
        pyautogui.click(self.non_block_time_point)
        SystemHotkey.copy_all()
        temp_all = pyperclip.paste()
        if "已传输大小" not in temp_all:
            return False
        content = temp_all.split("\n")[-2]
        content = content.replace(",", "")
        print(content)
        index1_s = content.find("已传输大小：")
        index1_e = content.find("kB耗时")
        if index1_s == -1 or index1_e == -1:
            return False
        content1 = content[index1_s + 6: index1_e].strip()
        index2_s = content.find("无阻塞时间：")
        index2_e = content.find("秒", index2_s)
        if index2_s == -1 or index2_e == -1:
            return False
        content2 = content[index2_s + 6: index2_e].strip()

        if content1 == "0" or content2 == "0":
            return False
        if content1 == last_data:
            print(f"{url}, 已传输大小: {content1} kB; 无阻塞时间: {content2} 秒")
            self.result_list.append((url, content1, content2))
            # self.res_file.write(f"{url},{content1},{content2}\n")
            return True
        self.data_map[index]["last_size"] = content1
        self.data_map[index]["last_time"] = content2
        return False

    def run(self):
        self.result_list = []

        def prepare_todo():
            self.open_pages(self.network_analyze_point)

        def fail_todo(url, current):
            item = self.data_map[current]
            if item["get_success"]: # 曾加载成功，但每次一直在增长（包括一次手动按p），可能是因为页面onShow会请求资源，导致每次都会增长，进而判定失败，这里直接使用最后一次的数值做处理。
                self.result_list.append((url, item["last_size"], item["last_time"]))
                return
            self.result_list.append((url, "超时", "超时"))
            # res_file.write(f"{url},超时,超时\n")
        try:
            super().run(prepare_todo, self._get_data, fail_todo)
        except KeyboardInterrupt:
            pass
        self.result_list = sorted(self.result_list, key=lambda t: t[0])
        result_name = "firefox_result.csv"
        res_file = open(RESULT_PATH + result_name, "w")
        res_file.write("url, size, time\n")
        for p in self.result_list:
            res_file.write(f"{p[0]}, {p[1]}, {p[2]}\n")
        res_file.close()
        # 关闭浏览器
        # browser.quit()

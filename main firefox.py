from selenium import webdriver
import time
import math
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import keyboard
import pyperclip
from conf import URLS_TXT_PATH

'''
    使用说明：
        首先安装依赖 pip install -r requirements.txt
        设定好下面的参数。
        运行后根据控制台提示进行操作。在设定两个鼠标点位后，将会自动运行。不断切换页面获取数据。当一个页面切换次数达到REFRESH_TIMES，需要手动操作后按p键继续。如果手动的次数达到REFRESH_ABORT次，再次需要手动操作时，将放弃此域名，后续可以手动测试。
        注意：一般造成手动的原因是页面禁止调试或可能请求google/facebook/youtube等网站，造成联不通，进而一直等待传输完毕（已传输大小一直为0k），需要点击“停止”按钮或“刷新”等到需要等待google时再“停止”，结果自然会显示，按p键继续即可。
'''

MAX_PAGES = 10 # 最多浏览器页数，同时打开的页面数量
REFRESH_TIMES = 10 # 需要手动进行操作时的切换次数
REFRESH_ABORT = 1 # 放弃该域名的手动操作次数

screenWidth, screenHeight = pyautogui.size()
windowLeft = screenWidth * 0.1
windowWidth, windowHeight = screenWidth * 0.5, screenHeight * 0.5
browser = webdriver.Firefox()
browser.set_window_rect(windowLeft, 0, windowWidth, windowHeight)
window_handles = []
data_map = [{
    "last_size": "0",
    "repeat_time": 0
} for i in range(MAX_PAGES)]


def open_pages(p1):
    for i in range(MAX_PAGES - 1):
        js = 'window.open("https://www.baidu.com");'
        browser.execute_script(js)
        time.sleep(1)
        pyautogui.hotkey("ctrl", "shift", "e")
        time.sleep(0.5)
        pyautogui.click(p1.x, p1.y)
        time.sleep(1)


def check_load_success():
    # 页面加载完成
    #wait = WebDriverWait(browser, 1)
    #wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # 判断页面是否完全加载
    if browser.execute_script("return document.readyState") == "complete":
        print("页面加载完成")
        return True
    else:
        print("页面加载未完成")
        return False


def get_mouse_position():
    browser.get('https://www.baidu.com')
    pyautogui.hotkey("ctrl", "shift", "e")
    print("将鼠标移动到启用性能分析（左下角秒表）上，按下p继续")
    time.sleep(1)
    keyboard.wait("p")
    p1 = pyautogui.position()
    # pyautogui.click(windowLeft + 10, windowHeight - 10)
    pyautogui.click(p1.x, p1.y)
    while not check_load_success():
        time.sleep(0.5)
    print("将鼠标移动到无阻塞时间上，按下p继续")
    keyboard.wait("p")
    p2 = pyautogui.position()
    print(p1, p2)
    return [p1, p2]


def open_url(url, handle):
    browser.switch_to.window(handle)
    browser.execute_script("window.location=\"https://" + url+"\"")
    print(f"URL: {url}")

def stop():
    # browser.quit()
    exit(1)

def get_data(coordinates, url, index, file):
    last_data = data_map[index]["last_size"]
    content1 = "0"
    content2 = "0"
    pyautogui.click(coordinates[1])
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
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

    if (content1 == "0" or content2 == "0"):
        return False
    if (content1 == last_data):
        print(f"{url}, 已传输大小: {content1} kB; 无阻塞时间: {content2} 秒")
        file.write(f"{url},{content1},{content2}\n")
        return True
    data_map[index]["last_size"] = content1
    return False


windows_urls = ["" for i in range(MAX_PAGES)]

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    keyboard.add_hotkey("s", stop)
    with open(URLS_TXT_PATH, "r") as file:
        urls = file.readlines()

    res_file = open("firefox_result.csv", "w")
    res_file.write("url, size, time")
    time_start_1 = time.time()
    coordinates = get_mouse_position()
    print("准备中")
    open_pages(coordinates[0])
    window_handles = browser.window_handles
    browser.switch_to.window(window_handles[0])
    time.sleep(0.2)
    total_round = math.ceil(len(urls) / MAX_PAGES)
    progress_index = 0
    opened_index = 0
    current = 0
    while progress_index < len(urls):
        # 检查页面池
        handle = None
        while handle is None:
            # 检查是否有可切换的页面
            current = (current + 1) % MAX_PAGES
            check_handle = window_handles[current]
            browser.switch_to.window(check_handle)
            check_url = windows_urls[current]
            print("切换到："+check_url)
            time.sleep(0.2)
            data_map[current]["repeat_time"] += 1
            if 0 == data_map[current]["repeat_time"] % REFRESH_TIMES:
                if REFRESH_ABORT+1 == data_map[current]["repeat_time"] // REFRESH_TIMES:
                    # 超过刷新上限，放弃
                    data_map[current] = {
                            "last_size": "0",
                            "repeat_time": 0
                        }
                    handle = check_handle
                    progress_index += 1
                    print(f"进度：{progress_index}/{len(urls)}")
                    res_file.write(f"{check_url},超时,超时\n")
                    break
                # 超过次数仍未加载成功，手动等待
                # open_url(check_url,check_handle)
                print("等待次数超限，按p继续")
                keyboard.wait("p")
            if check_load_success():
                if check_url != "":
                    if get_data(coordinates, check_url, current, res_file):
                        print(f"取数据成功，重复次数{data_map[current]["repeat_time"]}")
                        data_map[current] = {
                            "last_size": "0",
                            "repeat_time": 0
                        }
                        progress_index += 1
                        print(f"进度：{progress_index}/{len(urls)}")
                    else:
                       print(f"取数据存在变化，等待下一次，重复次数{data_map[current]["repeat_time"]}")
                       continue
                handle = check_handle
                break
        if opened_index < len(urls):
            url = urls[opened_index].strip()
            windows_urls[current] = url
            open_url(url, handle)
            opened_index += 1
        elif windows_urls[current] != "":
            windows_urls[current] = ""
            open_url("about:blank", handle)

        time.sleep(1)

    time_end_1 = time.time()
    print("运行时间："+str(time_end_1 - time_start_1)+"秒")
    res_file.close()
    # 关闭浏览器
    # browser.quit()

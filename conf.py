import os
FIREFOX_DRIVER_PATH = 'geckodriver.exe'
BIN_PATH = 'tracert'
URLS_TXT_PATH = "./url1.txt"
URLS_TXT_PATH2 = "./url2.txt"
SUDO_PASSWD = "111111"
RESULT_PATH = "./result/"

MAX_PAGES = 10  # 最多浏览器页数，同时打开的页面数量
REFRESH_TIMES = 10  # 需要手动进行操作时的切换次数
REFRESH_ABORT = 1  # 放弃该域名的手动操作次数

try:
    os.mkdir(RESULT_PATH)
except FileExistsError:
    pass
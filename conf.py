import os

# 通用设置
URLS_TXT_PATH = "./url1.txt"  # 域名列表，用于tcping/tracert
URLS_TXT_PATH2 = "./url2.txt"  # url资源列表，用于firefox
RESULT_PATH = "./result/"  # 结果保存文件夹
MAX_THREADS = 20  # tcping/tracert最多同时执行的线程数，太大可能导致系统处理不过来丢包，影响测试准确性。
SUDO_PASSWD = "111111"  # 如果在linux执行，需要su密码，windows无需设置
BIN_PATH = 'tracert'  # 弃用

# firefox设置
FIREFOX_DRIVER_PATH = 'geckodriver.exe'  # firefox驱动位置，默认无需更改
MAX_PAGES = 10  # 最多浏览器页数，同时打开的页面数量
REFRESH_TIMES = 8  # 需要手动进行操作时的切换次数
REFRESH_ABORT = 2  # 放弃该域名的手动操作次数 需要>自动尝试次数
REFRESH_AUTO = 1  # 自动修复尝试次数
REFRESH_AUTO_TIMES = 11  # 自动修复等待时间

try:
    os.mkdir(RESULT_PATH)
except FileExistsError:
    pass

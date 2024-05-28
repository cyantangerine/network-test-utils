import os
FIREFOX_DRIVER_PATH = 'old/geckodriver.exe'
BIN_PATH = 'tracert'
URLS_TXT_PATH = "./url1.txt"
SUDO_PASSWD = "111111"
RESULT_PATH = "./result/"
try:
    os.mkdir(RESULT_PATH)
except FileExistsError:
    pass
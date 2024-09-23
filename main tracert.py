import time

import operation
import threading
import subprocess
from util.net import check_ip_is_internet
from conf import URLS_TXT_PATH, RESULT_PATH, MAX_THREADS

start_time = time.time()
urls_file = open(URLS_TXT_PATH)
urls = urls_file.readlines()
result_name = RESULT_PATH + "/tracert_result.csv"
res_file = open(result_name, "w")
res_file.write("url, 首个非本地ip,, 跳\n")

mappings = {}
mappings_first = {}
mappings_name = {}
TOTAL = 0
CURRENT = 0
result_list = []


def print_process():
    print(f"总进度：{CURRENT}/{TOTAL}, {round(CURRENT / TOTAL * 100, 2)}%")


def cb(process: subprocess.Popen, output: str, index: int, args=None) -> operation.OperationResult:
    global CURRENT
    id = process.pid
    if id not in mappings:
        mappings[id] = []
        mappings_first[id] = ""
        mappings_name[id] = ""

    if index < 4:
        pass
        # if output.find("的路由")!= -1:
        #     mappings_name[id] = output[output.rfind("到") + 1: output.find("的路由：") - 5].strip()
        #     print(mappings_name[id])
    else:
        # if (output.find("跟踪完成") != -1):
        #
        # el
        if len(output) > 5:
            ip = output.split()[-1].strip()
            mappings[id].append(ip)
            if mappings_first[id] == "" and check_ip_is_internet(ip):
                mappings_first[id] = ip

                line_res = (args[0], mappings_first[id], ','.join(mappings[id]))
                result_list.append(line_res)
                res_file.write(f"{line_res[0]},{line_res[1]},{line_res[2]}\n")

                CURRENT += 1
                print_process()

                return True

from threading import Semaphore
semaphore = Semaphore(MAX_THREADS)
def processor(url, index):
    semaphore.acquire()
    operation.run_program_with_command_line(
        program='tracert',
        command=["/d" , '-d', url.strip()],
        cmd_callback=cb,
        args=[url.strip()]
    )
    semaphore.release()


threads = []
TOTAL = len(urls)
for (index, url) in enumerate(urls):
    # processor(url, index)
    t = threading.Thread(target=processor, args=[url, index])
    t.start()
    threads.append(t)

for t in threads:
    t.join()
res_file.close()
urls_file.close()
print("正在保存记录...")
# 对结果排序
result_list = sorted(result_list, key=lambda t: t[0])
res_file = open(result_name, "w")
res_file.write("url,首个非本地ip\n")
for p in result_list:
    res_file.write(f"{p[0]}, {p[1]}\n") # {p[2]}
res_file.close()
print(f"运行时间：{time.time()-start_time}s，结果已保存至{result_name}")

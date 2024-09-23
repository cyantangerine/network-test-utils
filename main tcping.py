import time
import operation
import threading
import subprocess
from conf import URLS_TXT_PATH, RESULT_PATH, MAX_THREADS

start_time = time.time()
urls_file = open(URLS_TXT_PATH)
urls = urls_file.readlines()
urls_file.close()

result_name = RESULT_PATH + "/tcping_result.csv"
res_file = open(result_name, "w")
res_file.write("url, latency, loss\n")
result_list = []

mappings = {}
mappings_first = {}
mappings_name = {}
TOTAL = 0
CURRENT = 0


def print_process():
    print(f"总进度：{CURRENT}/{TOTAL}, {round(CURRENT / TOTAL * 100, 2)}%")


def cb(process: subprocess.Popen, output: str, index: int, args=None) -> operation.OperationResult:
    url = args[0]
    global CURRENT
    id = process.pid
    if id not in mappings:
        mappings[id] = []
        mappings_first[id] = 99
        mappings_name[id] = url

    if mappings_first[id] == 99 and output.find("Ping statistics for") != -1:
        mappings_first[id] = index + 2
        print(f"=====RESULT FOR {url}=====")
    if index == mappings_first[id]:
        start_index = output.index("(") + 1
        end_index = output.index("%")
        loss = output[start_index:end_index]
        mappings[id].append(loss)
        print(f"====={url}:loss:{loss}=====")
        if round(float(loss), 0) == 100:
            mappings_first[id] -= 1
    elif index == mappings_first[id] + 2:
        if output.find("unable to connect") != -1:
            mappings[id].append("N/A")
        else:
            # Extract the latency value between "Average = " and "ms"
            start_index = output.index("Average = ") + len("Average = ")
            latency = output[start_index:-2]
            mappings[id].append(latency)
        print(f"====={url}:latency:{mappings[id][-1]}=====")

        line_res = (mappings_name[id], mappings[id][1].replace('ms', ''), mappings[id][0])
        result_list.append(line_res)
        res_file.write(f"{line_res[0]},{line_res[1]},{line_res[2]}\n")
        CURRENT += 1
        print_process()

from threading import Semaphore
semaphore = Semaphore(MAX_THREADS)
def processor(url, index):
    semaphore.acquire()
    operation.run_program_with_command_line(
        program='./tcping.exe',
        command=[f"-n", "20", "-g", "5", "-w", "1", url.strip(), "443"],
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
print("正在保存记录...")
# 对结果排序
result_list = sorted(result_list, key=lambda t: t[0])
res_file = open(result_name, "w")
res_file.write("url, latency, loss\n")
for p in result_list:
    res_file.write(f"{p[0]}, {p[1]}, {p[2]}\n")
res_file.close()
print(f"运行时间：{time.time()-start_time}s，结果已保存至{result_name}")


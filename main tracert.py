
import operation
import threading
import subprocess
import ipaddress
from util.net import check_ip_is_internet
from conf import URLS_TXT_PATH

urls_file = open(URLS_TXT_PATH)
urls = urls_file.readlines()
res_file = open("./tracert_result.csv", "w")
res_file.write("url, 首个非本地ip,, 跳\n")

mappings = {}
mappings_first = {}
mappings_name = {}
TOTAL = 0
CURRENT = 0

def print_process():
    print(f"总进度：{CURRENT}/{TOTAL}, {round(CURRENT/TOTAL*100, 2)}%")


def cb(process: subprocess.Popen, output: str, index: int, args = None)  -> operation.OperationResult:
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
        if(output.find("跟踪完成")!=-1):
            res_file.write(f"{args[0]},{mappings_first[id]},,{",".join(mappings[id])}\n")
            CURRENT+=1
            print_process()
        elif len(output) > 5:
            ip = output.split()[-1].strip()
            mappings[id].append(ip)
            if mappings_first[id] == "" and check_ip_is_internet(ip):
                mappings_first[id] = ip
                


def processor(url, index):
    operation.run_program_with_command_line(
        program='tracert',
        command=['-d', url.strip()],
        cmd_callback=cb,
        args=[url.strip()]
    )

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


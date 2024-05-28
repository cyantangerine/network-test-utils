import operation
import threading
import subprocess
from conf import URLS_TXT_PATH, RESULT_PATH

urls_file = open(URLS_TXT_PATH)
urls = urls_file.readlines()

res_file = open(RESULT_PATH + "/tcping_result.csv", "w")
res_file.write("url, latency, loss\n")

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

        res_file.write(f"{mappings_name[id]},{mappings[id][1].replace('ms', '')},{mappings[id][0]}\n")
        CURRENT += 1
        print_process()


def processor(url, index):
    operation.run_program_with_command_line(
        program='./tcping.exe',
        command=[f"-n", "20", "-g", "5", "-w", "1", url.strip(), "443"],
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

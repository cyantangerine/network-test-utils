import subprocess
import threading
from typing import Callable, Union, List, Tuple
from conf import BIN_PATH, SUDO_PASSWD
from util import platform


class OperationResult:
    def __init__(self, code: int, status: bool, message: str):
        self.code = code
        self.status = status
        self.message = message

    def __str__(self):
        return '{' + f"code: {self.code}, status: {self.status}, message: {self.message}" + '}'

    def __repr__(self):
        return self.__str__()


class OperationFailedType:
    WAITING_RESULT = -2
    UNKNWON_ERROR = -1
    SUCCESS = 0
    NO_PASSWORD_PROVIDED = 1
    PASSWORD_INCORRECT = 2
    CANT_FOUND_bin = 3


def __callback__print(process: subprocess.Popen, output: str, index: int, args=None):
    print(f"[{index}]输出：", output)


def __subthread_reading_worker(process: subprocess.Popen, callback: Callable[[subprocess.Popen, str, int], None]):
    index = 0
    while True:
        output = process.stdout.readline().decode("ansi")
        if output:
            callback(process, output, index)
        else:
            break
        index += 1


def __close_pipe_and_wait(process: subprocess.Popen, subthread: threading.Thread, do_not_raise_permission_error=False,
                          kill=False) -> int:
    try:
        if kill:
            process.terminate()
            print(f"process {process.pid} killed")
            # subthread.join()
        else:
            subthread.join()
            process.wait()
    except PermissionError:
        if (not do_not_raise_permission_error):
            # 当进程在sudo模式下运行时，无法终止进程，抛出异常
            raise PermissionError(
                "Process is running in root mode. Server can not terminate it. Try run server in root mode.")
    return process.returncode


def __open_pipe_with_multi_process(command: List[str],
                                   callback: Callable[[subprocess.Popen, str, int], None] = __callback__print) -> Tuple[
    subprocess.Popen, threading.Thread]:
    if command == None:
        raise ValueError("command is None")
    print("运行：", " ".join(command))
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    t = threading.Thread(target=__subthread_reading_worker,
                         args=(process, callback), daemon=True)
    t.start()
    return (process, t)


def check_sudo_password() -> OperationResult:
    """
    检查sudo密码是否正确

    Args:
        无

    Returns:
        OperationResult: 包含操作结果的类，包括code(操作结果码，NO_PASSWORD_PROVIDED表示未提供密码，PASSWORD_INCORRECT表示密码错误，SUCCESS表示密码正确，UNKNWON_ERROR表示未知错误)、status(操作状态，True表示成功，False表示失败)和message(操作结果信息)
    """
    global SUDO_PASSWD
    result = OperationResult(
        OperationFailedType.WAITING_RESULT, False, "waitting for progress")
    if (platform.get() == platform.PLATFORM_TYPE.WIN):
        result.code = OperationFailedType.SUCCESS
        result.status = True
        result.message = "password correct"
        return result

    def check_correct(process: subprocess.Popen, output: str, index: int):
        print(f"[{index}]输出：", output)
        nonlocal result
        # if(index != 1): return
        if (output.startswith('sudo: no password was provided')):
            result.code = OperationFailedType.NO_PASSWORD_PROVIDED
            result.status = False
            result.message = "no password was provided"
        elif (output.find('错误密码尝试') != -1 or output.find('incorrect password attempt') != -1):
            result.code = OperationFailedType.PASSWORD_INCORRECT
            result.status = False
            result.message = "password incorrect"
        elif (output.startswith('password correct')):
            result.code = OperationFailedType.SUCCESS
            result.status = True
            result.message = "password correct"
        else:
            result.code = OperationFailedType.UNKNWON_ERROR
            result.status = False
            result.message = output

    process, thread = __open_pipe_with_multi_process(
        ['sudo', '-S', 'echo', '"password correct"'], check_correct)
    try:
        process.stdin.write(str(SUDO_PASSWD).encode() + b'\n')
        process.stdin.close()
    except BrokenPipeError:
        pass
    returncode = __close_pipe_and_wait(process, thread, True)
    return result


def set_sudo_password(password: str):
    """
    临时设置sudo密码

    Args:
        password (str): sudo密码

    Returns:
        None
    """
    global SUDO_PASSWD
    SUDO_PASSWD = password


def __is_need_sudo() -> bool:
    if (platform.get() == platform.PLATFORM_TYPE.WIN):
        return False
    print("检查是否需要sudo权限")
    global SUDO_PASSWD
    result = None

    def get_result(process: subprocess.Popen, output: str, index: int):
        nonlocal result
        print(f"[{index}]输出：", output)
        if (output.find('do not need password') != -1):
            result = False
        else:
            result = True

    process, thread = __open_pipe_with_multi_process(
        ['sudo', '-S', 'echo', '"do not need password"'], get_result)
    try:
        process.stdin.close()
    except BrokenPipeError:
        pass
    returncode = __close_pipe_and_wait(process, thread, True)
    print("需要sudo权限?：", result)
    return result


def check_bin_exist() -> OperationResult:
    """
    检查bin是否存在

    Args:
        无

    Returns:
        OperationResult: 操作结果，包含操作是否成功、操作状态和操作信息

    """
    print("检查bin是否存在")
    global SUDO_PASSWD, BIN_PATH
    result = OperationResult(
        OperationFailedType.WAITING_RESULT, False, "waitting for progress")

    def check_correct(process: subprocess.Popen, output: str, index: int):
        print(f"[{index}]输出：", output, end="")
        nonlocal result
        if (output.find(' version ') != -1):
            result.code = OperationFailedType.SUCCESS
            result.status = True
            result.message = "OK"
        elif output.find('找不到命令') != -1 or output.find('command not found') != -1:
            result.code = OperationFailedType.CANT_FOUND_bin
            result.status = False
            result.message = "can not found bin in " + BIN_PATH
        else:
            result.code = OperationFailedType.UNKNWON_ERROR
            result.status = False
            result.message = output

    cmd = [BIN_PATH, '--version']
    if platform.get() != platform.PLATFORM_TYPE.WIN:
        arr = ['sudo', '-S']
        arr.extend(cmd)
        cmd = arr

    process, thread = __open_pipe_with_multi_process(
        cmd, check_correct)
    if platform.get() == platform.PLATFORM_TYPE.WIN:
        result.code = OperationFailedType.SUCCESS
        result.status = True
        result.message = "OK"
        return result
    if __is_need_sudo():
        process.stdin.write(str(SUDO_PASSWD).encode() + b'\n')
        process.stdin.close()
    returncode = __close_pipe_and_wait(process, thread, True)
    return result


class Cmd_Callback:
    Union[Callable[[subprocess.Popen, str, int, None], Union[OperationResult, None]], None]


def run_root_with_command_line(command: List[str], cmd_callback: Cmd_Callback = None) -> OperationResult:
    """
    运行bin命令行

    Args:
        command (List[str]): 运行bin命令行需要使用的参数
        cmd_callback (Callable[[subprocess.Popen, str, int], OperationResult or None]): 回调函数，用于处理命令行输出和进程结果

    Returns:
        OperationResult: 包含命令执行结果的结构体对象

    """
    print("运行bin")
    global SUDO_PASSWD, BIN_PATH
    result = OperationResult(
        OperationFailedType.WAITING_RESULT, False, "waitting for progress")

    def check_correct(process: subprocess.Popen, output: str, index: int):
        print(f"[{index}]输出：", output, end="")
        nonlocal result
        if cmd_callback is None:
            return
        resref = cmd_callback(process, output, index)
        if resref is None:
            return
        # 这里可以做一些事情
        result.code = resref.code
        result.status = resref.status
        result.message = resref.message

    c = ['sudo', '-S', BIN_PATH]
    c.extend(p for p in command)
    process, thread = __open_pipe_with_multi_process(c, check_correct)
    if __is_need_sudo():
        process.stdin.write(str(SUDO_PASSWD).encode() + b'\n')
        process.stdin.close()
    returncode = __close_pipe_and_wait(process, thread, True)
    result.code = returncode
    result.status = returncode == 0
    result.message = ""
    return result


def run_program_with_command_line(program: str = BIN_PATH, command: List[str] = [], cmd_callback: Cmd_Callback = None,
                                  pid_ref=[], args=[""]) -> OperationResult:
    """
    运行命令行

    Args:
        command (List[str]): 运行命令行需要使用的参数
        cmd_callback (Callable[[subprocess.Popen, str, int], OperationResult or None]): 回调函数，用于处理命令行输出和进程结果

    Returns:
        OperationResult: 包含命令执行结果的结构体对象

    """
    print("运行")
    result = OperationResult(
        OperationFailedType.WAITING_RESULT, False, "waitting for progress")

    def check_correct(process: subprocess.Popen, output: str, index: int):
        print(f"[{process.pid},{index},{args[0]}]输出：", output, end="")
        nonlocal result
        if cmd_callback is None:
            return
        resref = cmd_callback(process, output, index, args)
        if resref is None:
            return
        if resref:
            __close_pipe_and_wait(process, thread, True, True)
        # 这里可以做一些事情
        #result.code = resref.code
        #result.status = resref.status
        #result.message = resref.message

    c = [program]
    c.extend(p for p in command)
    process, thread = __open_pipe_with_multi_process(c, check_correct)
    print(f"PID:{process.pid}")
    pid_ref.append(process.pid)
    if __is_need_sudo():
        process.stdin.write(str(SUDO_PASSWD).encode() + b'\n')
        process.stdin.close()
    returncode = __close_pipe_and_wait(process, thread, True)
    result.code = returncode
    result.status = returncode == 0
    result.message = ""
    return result


__all__ = [check_sudo_password, set_sudo_password, run_root_with_command_line, check_bin_exist,
           OperationResult, OperationFailedType, run_program_with_command_line]

if __name__ == "__main__":
    print(check_sudo_password())
    print(__is_need_sudo())
    print(check_bin_exist())

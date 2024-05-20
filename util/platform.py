import sys


class PLATFORM_TYPE:
    WIN = 0
    MAC = 1
    LINUX = 2
    UNKNOWN = -1


platform_type = PLATFORM_TYPE.UNKNOWN

if sys.platform == 'win32':
    print('This is Windows platform')
    platform_type = PLATFORM_TYPE.WIN
elif sys.platform == 'darwin':
    print('This is MacOS platform')
    platform_type = PLATFORM_TYPE.MAC
elif sys.platform == 'linux':
    print('This is Linux platform')
    platform_type = PLATFORM_TYPE.LINUX
else:
    print('Unknown platform')


def get():
    global platform_type
    return platform_type

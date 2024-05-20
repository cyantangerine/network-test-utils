import ipaddress
# 判断ip是内网还是外网
def check_ip_is_internet(ip):
    try:
        return not ipaddress.ip_address(ip.strip()).is_private
    except Exception as e:
        print(e)
        return False
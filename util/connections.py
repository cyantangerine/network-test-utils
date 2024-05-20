import json

ENABLE_DETAIL_FALSE = True # 是否返回client错误详情，关闭则返回服务器内部错误


class RequestData:
    def __init__(self, source):
        if source:
            self.data = json.loads(source)
        else:
            raise Exception("请求数据为空")

    def get(self, key: str, emptyable=False):
        val = self.data.get(key)
        if val is None and not emptyable:
            print("原始数据：", self.data)
            raise Exception("在JSON中读取" + key + "时出错")
        else:
            return val


def load_request_data(request):
    source = request.body.decode("utf-8")
    print("收到数据：", source)
    return RequestData(source)


def build_response(info="OK", success=False, data=None):
    if not success and info == 'OK' and not ENABLE_DETAIL_FALSE:
        info = "服务器内部错误"
    result = {
        'status': success,
        'errMsg': info,
        'data': data
    }

    print(repr(data))
    result = json.dumps(result, ensure_ascii=False)
    return result

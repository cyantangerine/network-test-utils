'''
    使用说明：
        运行后根据控制台提示进行操作。在设定两个鼠标点位后，将会自动运行。不断切换页面获取数据。当一个页面切换次数达到REFRESH_TIMES，需要手动操作后按p键继续。如果手动的次数达到REFRESH_ABORT次，再次需要手动操作时，将放弃此域名，后续可以手动测试。
        注意：一般造成手动的原因是页面禁止调试或可能请求google/facebook/youtube等网站，造成联不通，进而一直等待传输完毕（已传输大小一直为0k），需要点击“停止”按钮或“刷新”等到需要等待google时再“停止”，结果自然会显示，按p键继续即可。

        千万不能关闭创建的页面。
        如果页面不能打开，请p键继续后等待自动放弃。

        开始时将打开MAX_PAGES个百度，同时打开开发者工具，请不要操作，打开完毕后自动开始测试。
'''
import pyautogui
from firefox.time import FirefoxTimeOperator

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    fx = FirefoxTimeOperator()
    fx.run()

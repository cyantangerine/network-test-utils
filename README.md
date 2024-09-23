### 网络数据库连通性测试工具
如果有更好的建议，欢迎提交issues和pull request！
如果觉得好用，麻烦点个star~谢谢

共包含4个测试工具，包括tcping, tracert, firefox的加载速度和DOMC加载时间。

#### 使用方法：
1. 如果有git可以复制链接进行clone（推荐，下载Github desktop，方便后续版本更新），没有可以点击绿色code按钮-下载zip解压到电脑中。
2. 安装Python 3.7及以上版本或使用VS Code的Python扩展。
3. win+R，输入cmd（打开命令提示符），cd切换到源码文件夹位置，输入
   ```shell
    cd /d 代码文件夹位置
   ```
   ```shell
    pip install -r requirements.txt 
   ```
4. 打开Python IDLE 或 VS Code 或 命令提示符终端。
5. 运行main xx.py。xx是指当前测试项。
   在vscode和idle中可以直接点击运行。
   在终端中需要输入命令运行。
   ```shell
    python "main xx.py"
   ```
6. 单项测试完成后，结果将会保存到conf.py设定的结果文件夹中（默认为代码文件夹中的result）。如果测试卡住，在终端或idle中可以按ctrl+c强行停止测试，测试结果可能不完整。
7. 四项测试完成后，可以均按url字母升序排序，放入到测试结果表格中。
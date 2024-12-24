# 整合四项测试结果为一个文件，方便粘贴到测试表格中，直接运行即可
import time

import pandas as pd
from conf import RESULT_PATH

df_domc = pd.read_csv(RESULT_PATH + "/firefox_domc_result.csv", encoding='gbk')
df_fire = pd.read_csv(RESULT_PATH + "/firefox_result.csv", encoding='gbk')
df_domc['url'] = df_domc['url'].str.replace('ebookcentral.proquest.com/lib/hit/', 'ebookcentral.proquest.com')
df_fire['url'] = df_fire['url'].str.replace('ebookcentral.proquest.com/lib/hit/', 'ebookcentral.proquest.com')
df_tcping = pd.read_csv(RESULT_PATH + "/tcping_result.csv", encoding='gbk')
df_tracert = pd.read_csv(RESULT_PATH + "/tracert_result.csv", encoding='gbk', usecols=[0, 1])

result = pd.merge(df_tracert, df_tcping, on='url', how='outer')
result = pd.merge(result, df_fire, on='url', how='outer')
result = pd.merge(result, df_domc, on='url', how='outer')

result.insert(4, 'kBps', result[" size"]/result[' time'])

print(result)
result.to_excel(RESULT_PATH + f"/results_{time.strftime('%Y%m%d%H%M%S', time.localtime())}.xlsx", index=False)

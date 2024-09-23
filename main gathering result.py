# 整合四项测试结果为一个文件，方便粘贴到测试表格中
import pandas as pd
from conf import RESULT_PATH

df_domc = pd.read_csv(RESULT_PATH + "/firefox_domc_result.csv", encoding='gbk')
df_fire = pd.read_csv(RESULT_PATH + "/firefox_result.csv", encoding='gbk')
df_tcping = pd.read_csv(RESULT_PATH + "/tcping_result.csv", encoding='gbk')
df_tracert = pd.read_csv(RESULT_PATH + "/tracert_result.csv", encoding='gbk', usecols=[0, 1])

result = pd.merge(df_domc, df_fire, on='url', how='outer')
result = pd.merge(result, df_tcping, on='url', how='outer')
result = pd.merge(result, df_tracert, on='url', how='outer')


print(result)
result.to_excel(RESULT_PATH + "/results.xlsx", index=False)

#coding=utf-8
# ==============================================================================
"""数据清洗
版本：
    Python：3.6.7
参考：
    https://www.gushiwen.org/
将爬取到的古诗词数据进行清洗，包括content注释部分的清除，特殊符号的清除，换行符等清除，
最终目标是将content转换为一行的仅包含中文、标点符号的内容。
"""
#%%
import pandas as pd
import re
# read_csv不能直接读路径，需要赋给path再读，很奇怪
path = r'E:\pythonprojects\craft\code\RNN\shici.csv'
df = pd.read_csv(path)
df.head(5)

# VSCode使用#%%可以将代码划分为cell，直接可以运行，等同于jupyter notebook
#%%
# 需要将content中的一些特殊符号删掉或者转换为其他字符，比如换行符\n删掉，
# 各种括号转换为英文括号然后通过正则式删除，需要使用re进行转换
symbol_dict = {'\n': '', ' ': '', '\u3000': '', '\ue112': '', '\ue83d': '',
    '\ue85d': '', '\ue85f': '', '〖': '', '𬞞': '', '②': '',
    '■': '', '□': '', '◇': '', '#': '', '＊': '', '＿': '',
    '<': '', '>': '', '¤': '', 'á': '', 'è': '', 'ì': '',
    'í': '', 'ù': '', '—': '', '﹑': ',', '!': '！', ':': '：',
    '．': '.', '?': '？', '‘': "'", ',': '，', '.': '。', 
    '’': "'", '“': '"', '”': '"', ';': '；', '（': '(', '）': ')',
    '【': '(', '】': ')', '〔': '(', '〕': ')', '·': ''}
# 生成re的pattern，symbol_format是处理特殊字符替换的pattern
rep = {re.escape(k): v for k, v in symbol_dict.items()}
symbol_format = re.compile('|'.join(rep.keys()))
def process_data(data):
    """利用正则式以及re处理数据，结合DataFrame.apply使用
    Args:
        data: 输入数据str
    Returns:
        data: 处理完成后的数据str
    """
    # 第一步特殊字符转换
    data = symbol_format.sub(lambda x: rep[re.escape(x.group(0))], data)
    # 第二步删除括号及括号中的所有内容
    data = re.sub(u"\\{.*?\\}|\\[.*?\\]|\\(.*?\\)", "", data)
    # 第三步删除大小写字母及数字
    data = re.sub(r'[a-zA-Z0-9]+', '', data)
    return data
# 依照上述过程清洗数据，使用apply
df['content'] = df['content'].apply(process_data)

# 将清洗完成后的content转换为set和list，set用于确定字典，list用于确定特征向量
# 这里就直接保存在原始数据中了，便于对比
set_format = lambda x: set(x)
list_format = lambda x: list(x)

df['content_set'] = df['content'].map(set_format)
df['content_list'] = df['content'].map(list_format)
df.head(5)
#%%
df.to_csv('data.csv', index=0) # index=0表示不保存索引


#%%

zi = set()
for i in range(len(df)):
    zi = zi.union(df['content_set'][i])
 
l = list(zi)
l.sort()
print(len(l))





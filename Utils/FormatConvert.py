# encoding=utf8
import re
import datetime

#中文日期格式转换成标准的格式
def date_conversion(datetime):
    datetimeList = datetime.split(' ')
    if datetimeList.__len__()==0:
        return None
    date = datetimeList[0]
    time = ""
    if datetimeList.__len__() == 2:
        time = datetimeList[1]
    '''将中文日期转换成自己想要的格式如：2018年09月29日转换成2018-09-29'''
    ls=re.findall(r'(.*)年(.*)月(.*)日', date)
    if ls.__len__()==0:
        return None
    c = list(ls[0])
    new_date = ''
    # print(c)
    if len(c[1]) < 2:
        c[1] = '0' + c[1]
        # print('-'.join(c))
        new_date = '-'.join(c)
    else:
        # print('-'.join(c))
        new_date = '-'.join(c)
    return new_date + ' ' + time


# print(date_conversion('2018年09月29日'))
# str=date_conversion('2018年09月29日')
# d=datetime.datetime.strptime('2018-10-15 20:00:00', "%Y-%m-%d  %H:%M:%S")
# dd=datetime.datetime.now()+datetime.timedelta(days=1)
# print(dd)
# print(d)
# print('2018-10-15 10:00:00'>'2018-10-15 10:00:00')
# str='2018-10-15'
# d=datetime.datetime.strptime(str,"%Y-%m-%d")+datetime.timedelta(days=1)
# print(d)
# dd=datetime.datetime.now()
# print(dd)
# print(dd>d)
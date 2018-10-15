from urllib import request, parse

# GET - 直接打开url
# response = request.urlopen(url)

# 添加请求头，模仿浏览器
req = request.Request("https://cuiqingcai.com/1319.html")
#http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx
req = request.Request("http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx")
req.add_header('User-Agent', 'Mozilla/6.0')
response = request.urlopen(req)

# POST - 添加请求数据
# login_data = parse.urlencode([
#     ('username', email),
#     ('password', passwd),
# ])
# req = request.Request(url)
# req.add_header('User-Agent', 'Mozilla/6.0')
# response = request.urlopen(req, data=login_data.encode('utf-8'))

content = response.read()

from bs4 import BeautifulSoup

# html.parser, lxml, xml, html5lib不同的解析器类型
soup = BeautifulSoup(content, "html.parser", from_encoding='utf-8')

#print( soup.prettify())
tableData=soup.find('table',class_='tableDataTable')
# print(tableData)
# print(tableData.find('tr'))
trs=tableData.find_all('tr')
for tr in trs:
    # print(tr.find_all('td'))
    #print(tr.find_all('td')[0].text)
    tds=tr.find_all('td')
    for td in tds:
        print(td.text,end=' | ')
    print()

# for dirs in listData:
#     for key in dirs:
#         print(key,dirs[key],end=' | ')
#     print()
#
# print(listData[0]['currency'])
# 2018年10月11日 21:28:02
# print(datetime.datetime.strptime("2016年-06-22", "%年-%m-%d"))
# print(datetime.date()('2018年10月11日 18:51:33'))

# # 查找标签
# node = soup.find('p')
# # 查找class
# node = soup.find_all('div', class_='container-inner')
# print(type(node))
# print(node)
# print('------------------')
# spans=node[0].find_all("span")
# # print(node[0].find_all("span"))
# for spanText in spans:
#     print(spanText.text)
# encoding=utf8
from urllib import request, parse
from Spider.SpiderBase import SpiderBase
from bs4 import BeautifulSoup
from Utils import FormatConvert,ValidateData


# 添加请求头，模仿浏览器
# req = request.Request("https://cuiqingcai.com/1319.html")
# req = request.Request("http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx")
# req.add_header('User-Agent', 'Mozilla/6.0')
# response = request.urlopen(req)

#汇率报价爬虫
class ExchangeRateQuotationWeb(SpiderBase):

    def __init__(self,url):
        #SpiderBase.__init__(self,url)
        super(ExchangeRateQuotationWeb,self).__init__(url)
    def spider(self):
        # html.parser, lxml, xml, html5lib不同的解析器类型
        soup = BeautifulSoup(self.content, "html.parser", from_encoding='utf-8')
        # print( soup.prettify())
        tableData = soup.find('table', class_='tableDataTable')
        trs = tableData.find_all('tr')
        # 币种 | 现汇买入价 | 现钞买入价 | 现汇卖出价 | 现钞卖出价 | 发布时间 |
        # currency, spotPurchasePrice, cashPurchasePrice, spotSellingPrice, cashSellingPrice, issuingTime
        trs.pop(0)  # 排除第一行
        listData = []
        for tr in trs:
            tds = tr.find_all('td')
            dir = {}
            # 币种
            dir['currency'] = tds[0].text
            #  strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列：
            # 现汇买入价
            if tds[1].text.strip() and ValidateData.isdecimal(tds[1].text):
                dir['spotPurchasePrice'] = tds[1].text
            # 现钞买入价
            if tds[2].text.strip() and ValidateData.isdecimal(tds[2].text):
                dir['cashPurchasePrice'] = tds[2].text
            # 现汇卖出价
            if tds[3].text.strip() and ValidateData.isdecimal(tds[3].text):
                dir['spotSellingPrice'] = tds[3].text
            # 现钞卖出价
            if tds[4].text.strip() and ValidateData.isdecimal(tds[4].text):
                dir['cashSellingPrice'] = tds[4].text
            # 发布时间
            if tds[5].text.strip():
                dir['issuingTime'] = FormatConvert.date_conversion(tds[5].text)
            listData.append(dir)
        return listData

# aa=ExchangeRateQuotationWeb("http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx")
# for d in aa.spider():
#     print(d)


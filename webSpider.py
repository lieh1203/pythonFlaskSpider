# encoding=utf-8
from flask import request
import config
import os
from Spider import SpiderWeb
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app.models import ExchangeRateQuotation
import warnings
from app import ResultDtos
import datetime

warnings.filterwarnings("ignore")

# $ export FLASK_APP=hello
# $ flask run

# > set FLASK_APP=hello
# > flask run
#修改环境变量，修改数据库连接
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    return 'index'


# 批处理调用，导入爬取的汇率数据，工商银行
@app.route('/schedule/importexchangeratequotation/<mechanismCode>', methods=['get'])
def spiderExchangeRateQuotation(mechanismCode): #'ICBC'
    aa = SpiderWeb.ExchangeRateQuotationWeb(config.spiderUrls['QuotationUrl'])
    result = aa.spider()
    now_time = datetime.datetime.now()
    for dir in result:
        quotation = ExchangeRateQuotation(currency=dir.get('currency'), spotPurchasePrice=dir.get('spotPurchasePrice'),
                                          cashPurchasePrice=dir.get('cashPurchasePrice'),
                                          spotSellingPrice=dir.get('spotSellingPrice'),
                                          cashSellingPrice=dir.get('cashSellingPrice'),
                                          issuingTime=dir.get('issuingTime'),acquisitionTime=now_time,
                                          mechanismCode=mechanismCode)
        db.session.add(quotation)
        db.session.commit()
        db.session.close()
    return 'ok'


# 获取汇率数据，根据issuingTime查询
@app.route('/exchangerate/getexchangeratequotationlist', methods=['get'])
def getexchangeratequotationlist():
    # pageindex = request.args.get('pageindex')
    # pagecount = request.args.get('pagecount')
    issuingBeginTime = request.args.get('issuingBeginTime')
    issuingEndTime = request.args.get('issuingEndTime')
    data = None
    # if pageindex is None:
    #     pageindex = 1
    # else:
    #     pageindex = int(pageindex)
    # if pagecount is None:
    #     pagecount = 10
    # else:
    #     pagecount = int(pagecount)
    param = []
    #d=datetime.datetime.strptime(str,"%Y-%m-%d")+datetime.timedelta(days=1)
    if issuingBeginTime:
        #print(db.cast(issuingBeginTime, db.Date))
        #param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) >= db.cast(issuingBeginTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime>= datetime.datetime.strptime(issuingBeginTime,"%Y-%m-%d"))
    if issuingEndTime:
        #param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) < db.cast(issuingEndTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime < datetime.datetime.strptime(issuingEndTime,"%Y-%m-%d")+datetime.timedelta(days=1))
    print(param)
    #data = ExchangeRateQuotation.query.filter(*param)
     #db.func.max(ExchangeRateQuotation.acquisitionTime)
    items=[]
    # 如果不输入参数，返回最后一次导入(acquisitionTime)的那批数据
    maxAcquisitionTime = db.session.query(db.func.max(ExchangeRateQuotation.acquisitionTime)).filter(*param).first()
    if maxAcquisitionTime[0]:
        data=ExchangeRateQuotation.query.filter(ExchangeRateQuotation.acquisitionTime == maxAcquisitionTime[0])
        print(maxAcquisitionTime[0])
    if data:
        items = data.all()
    #totalCount = ExchangeRateQuotation.query.count()
    # dataPaged = data.paginate(page=pageindex, per_page=pagecount, error_out=False)
    # print(dataPaged)
    #r = ResultDtos.PagedResultDto(totalCount=totalCount, items=dataPaged.items)
    r=ResultDtos.NonPagedResultDto(items=items)
    #app.logger.info(param)
    #print(r.data)
    return r.data


@app.after_request
def after_request(response):

    return response


if __name__ == '__main__':
    app.run(debug=True)
    #manager.run()

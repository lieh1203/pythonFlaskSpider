# -*- coding: utf-8 -*-
from flask import request
import config
import os
from Spider import SpiderWeb
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app.models import ExchangeRateQuotation, Fund
import warnings
from app import ResultDtos
import datetime
import logging
from flask_cors import *
import urllib3
import json

warnings.filterwarnings("ignore")

from logging.config import dictConfig

dictConfig({'version': 1,
            'formatters': {'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }},
            'handlers': {
                'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': 'log/app.log',
                    'maxBytes': 5024,
                    'backupCount': 3,
                    'encoding': 'utf-8'
                }
            },
            'root': {'level': 'INFO',
                     'handlers': ['wsgi', 'file'],
                     }
            })

# $ export FLASK_APP=hello
# $ flask run

# > set FLASK_APP=hello
# > flask run
# 修改环境变量，修改数据库连接
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
fundKey = config.config[os.getenv('FLASK_CONFIG') or 'default'].fundKey
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
# 跨域
CORS(app, supports_credentials=True)


@app.route('/')
def index():
    return 'index'


@app.route('/scheduleconfirm')
def scheduleconfirm():
    now_time = datetime.datetime.now()
    str = u'批处理调用确认，调用时间：{time}'.format(time=now_time)
    app.logger.info(str)
    return str


# 批处理调用，导入爬取的汇率数据，工商银行
@app.route('/schedule/importexchangeratequotation/<mechanismCode>', methods=['get'])
def spiderExchangeRateQuotation(mechanismCode):  # 'ICBC'
    aa = SpiderWeb.ExchangeRateQuotationWeb(config.spiderUrls['QuotationUrl'])
    result = aa.spider()
    now_time = datetime.datetime.now()
    for dir in result:
        quotation = ExchangeRateQuotation(currency=dir.get('currency'), spotPurchasePrice=dir.get('spotPurchasePrice'),
                                          cashPurchasePrice=dir.get('cashPurchasePrice'),
                                          spotSellingPrice=dir.get('spotSellingPrice'),
                                          cashSellingPrice=dir.get('cashSellingPrice'),
                                          issuingTime=dir.get('issuingTime'), acquisitionTime=now_time,
                                          mechanismCode=mechanismCode)
        db.session.add(quotation)
        db.session.commit()
        db.session.close()
    return 'ok'


# 获取汇率数据，根据issuingTime查询
@app.route('/exchangerate/getexchangeratequotationlist', methods=['get'])
def getexchangeratequotationlist():
    # app.logger.info(u'getexchangeratequotationlist')
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
    # d=datetime.datetime.strptime(str,"%Y-%m-%d")+datetime.timedelta(days=1)
    if issuingBeginTime:
        # print(db.cast(issuingBeginTime, db.Date))
        # param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) >= db.cast(issuingBeginTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime >= datetime.datetime.strptime(issuingBeginTime, "%Y-%m-%d"))
    if issuingEndTime:
        # param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) < db.cast(issuingEndTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime < datetime.datetime.strptime(issuingEndTime,
                                                                                    "%Y-%m-%d") + datetime.timedelta(
            days=1))
    print(param)
    # data = ExchangeRateQuotation.query.filter(*param)
    # db.func.max(ExchangeRateQuotation.acquisitionTime)
    items = []
    # 如果不输入参数，返回最后一次可能有时分秒的差别）导入(acquisitionTime)的那批数据
    maxAcquisitionTime = db.session.query(db.func.max(ExchangeRateQuotation.acquisitionTime)).filter(*param).first()
    if maxAcquisitionTime[0]:
        data = ExchangeRateQuotation.query.filter(ExchangeRateQuotation.acquisitionTime == maxAcquisitionTime[0])
        print(maxAcquisitionTime[0])
    if data:
        items = data.all()
    # totalCount = ExchangeRateQuotation.query.count()
    # dataPaged = data.paginate(page=pageindex, per_page=pagecount, error_out=False)
    # print(dataPaged)
    # r = ResultDtos.PagedResultDto(totalCount=totalCount, items=dataPaged.items)
    r = ResultDtos.NonPagedResultDto(items=items)
    # app.logger.info(param)
    # print(r.data)

    return r.data

#导入基金数据，批处理调用
@app.route('/funds/importfunds')
def importfunds():
    http = urllib3.PoolManager()
    url = 'https://mptest.fofinvesting.com/wxapi/third/fundlist?key={0}'.format(fundKey)
    app.logger.info(url)
    r = http.request('get', url)
    dataJson = json.loads(r.data.decode('utf-8'))
    app.logger.info(dataJson)
    inserted_funds = []
    if dataJson.get('status') and dataJson.get('status') == 'error':
        return '没有权限或接口异常'
    else:
        if dataJson.get('amount') and dataJson.get('amount') > 0:
            funds = dataJson.get('funds')
            for f in funds:
                code = f.get('code')
                title = f.get('title')
                category = f.get('category')
                annualizedRate = f.get('annualizedRate')
                unitNav = f.get('unitNav')
                navDate = f.get('navDate')
                subCategory = f.get('subCategory')
                acquisitionTime = datetime.datetime.now()
                inserted_funds.append(Fund(code=code, title=title, category=category, annualizedRate=annualizedRate,
                                           unitNav=unitNav, navDate=navDate, subCategory=subCategory,
                                           acquisitionTime=acquisitionTime,mechanismCode='channel')) #况客基金
    db.session.add_all(inserted_funds)
    db.session.commit()
    db.session.close()
    return 'ok'


@app.route('/funds')
def getfoudListByPaged():
    pageindex = request.args.get('pageindex')
    pagecount = request.args.get('pagecount')
    acquisitionTime = request.args.get('acquisitionTime')
    code = request.args.get('code')
    data = None
    if pageindex is None:
        pageindex = 1
    else:
        pageindex = int(pageindex)
    if pagecount is None:
        pagecount = 10
    else:
        pagecount = int(pagecount)
    params = []

    if code:
        params.append(Fund.code == code)

    if acquisitionTime:
        params.append(db.cast(Fund.acquisitionTime ,db.Date) == db.cast(acquisitionTime ,db.Date))
        #params.append(Fund.acquisitionTime == datetime.datetime.strptime(acquisitionTime, "%Y-%m-%d"))
    else:  # 默认最后一天的行情，批量插入时，可能会有时分秒的差异，所以要以date格式查询，如果一天中导入多次，会查询出重复数据
        acquisitionTime = db.session.query(db.func.max(Fund.acquisitionTime)).first()
        if acquisitionTime[0]:
            params.append(db.cast(Fund.acquisitionTime ,db.Date) == db.cast(acquisitionTime[0], db.Date))
            #params.append(Fund.acquisitionTime == acquisitionTime[0])

    data = Fund.query.filter(*params)
    totalCount = data.count()

    dataPaged = data.paginate(page=pageindex, per_page=pagecount, error_out=False)
    app.logger.info(dataPaged)
    r = ResultDtos.PagedResultDto(totalCount=totalCount, items=dataPaged.items)
    return r.data


@app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    app.run()
    #manager.run()

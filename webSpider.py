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
    dicts = request.args.to_dict()
    issuingBeginTime = None
    issuingEndTime = None
    orgcode = None  # 机构code
    for d in dicts:  # 忽略大小写
        if 'issuingbeginTime'.lower() == d.lower():
            issuingBeginTime = dicts.get(d)
        if 'issuingendTime'.lower() == d.lower():
            issuingEndTime = dicts.get(d)
        if 'orgcode'.lower() == d.lower():
            orgcode = dicts.get(d)

    data = None
    param = []

    if orgcode:
        param.append(ExchangeRateQuotation.mechanismCode == orgcode)

    if issuingBeginTime:
        # param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) >= db.cast(issuingBeginTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime >= datetime.datetime.strptime(issuingBeginTime, "%Y-%m-%d"))

    if issuingEndTime:
        # param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) < db.cast(issuingEndTime, db.Date))
        param.append(ExchangeRateQuotation.issuingTime < datetime.datetime.strptime(issuingEndTime,
                                                                                    "%Y-%m-%d") + datetime.timedelta(
            days=1))

    items = []
    # 如果不输入参数，返回最后一次（可能有时分秒的差别）导入(acquisitionTime)的那批数据
    maxAcquisitionTime = db.session.query(db.func.max(ExchangeRateQuotation.acquisitionTime)).filter(*param).first()
    if maxAcquisitionTime[0]:
        param.append(ExchangeRateQuotation.acquisitionTime == maxAcquisitionTime[0])

    data = ExchangeRateQuotation.query.filter(*param)
    if data:
        items = data.all()

    r = ResultDtos.NonPagedResultDto(items=items)
    return r.data


# 导入基金数据，批处理调用
@app.route('/funds/importfunds')
def importfunds():
    http = urllib3.PoolManager()
    fundKey = config.config[os.getenv('FLASK_CONFIG') or 'default'].fundKey
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
            now_time = datetime.datetime.now()
            for f in funds:
                code = f.get('code')
                title = f.get('title')
                category = f.get('category')
                annualizedRate = f.get('annualizedRate')
                unitNav = f.get('unitNav')
                navDate = f.get('navDate')
                subCategory = f.get('subCategory')
                inserted_funds.append(Fund(code=code, title=title, category=category, annualizedRate=annualizedRate,
                                           unitNav=unitNav, navDate=navDate, subCategory=subCategory,
                                           acquisitionTime=now_time, mechanismCode='fof'))  # fof 况客基金code
    db.session.add_all(inserted_funds)
    db.session.commit()
    db.session.close()
    return 'ok'


# 获取基金数据列表
@app.route('/funds')
def getfoudListByPaged():
    dicts = request.args.to_dict()
    pageindex = None
    pagesize = None
    acquisitionTime = None
    code = None
    orgcode = None  # 机构code

    for d in dicts:  # 忽略大小写
        if 'pageindex'.lower() == d.lower():
            pageindex = dicts.get(d)
        if 'pagesize'.lower() == d.lower():
            pagesize = dicts.get(d)
        if 'time'.lower() == d.lower():
            acquisitionTime = dicts.get(d)
        if 'code'.lower() == d.lower():
            code = dicts.get(d)
        if 'orgcode'.lower() == d.lower():
            orgcode = dicts.get(d)

    data = None
    if pageindex is None:
        pageindex = 1
    else:
        pageindex = int(pageindex)
    if pagesize is None:
        pagesize = 10
    else:
        pagesize = int(pagesize)

    # 拼接查询条件参数数组
    params = []

    if code:
        params.append(Fund.code == code)

    if orgcode:
        params.append(Fund.mechanismCode == orgcode)

    if acquisitionTime: #比较日期格式，不匹配时分秒格式
        params.append(db.cast(Fund.acquisitionTime, db.Date) == db.cast(acquisitionTime, db.Date))

    # 默认最后一天的行情
    max_acquisitionTime = db.session.query(db.func.max(Fund.acquisitionTime)).filter(*params).first()
    if max_acquisitionTime[0]:
        params.append(Fund.acquisitionTime == max_acquisitionTime[0])

    data = Fund.query.filter(*params)
    totalCount = data.count()

    dataPaged = data.paginate(page=pageindex, per_page=pagesize, error_out=False)
    app.logger.info(dataPaged)
    r = ResultDtos.PagedResultDto(totalCount=totalCount, items=dataPaged.items)
    return r.data


@app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    app.run()
    #manager.run()

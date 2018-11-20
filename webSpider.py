# -*- coding: utf-8 -*-
from flask import request
import config
import os
from Spider import SpiderWeb
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app, orm, cache
from app.models import ExchangeRateQuotation, Fund, FundNetValue, Category, SubCategory
import warnings
from app import ResultDtos
import datetime
import logging
from flask_cors import *
import urllib3
import json
from logging.config import dictConfig
import urllib
import time
from dateutil.relativedelta import relativedelta
import re

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
                    'filename': 'app_log/my_app.log',
                    'maxBytes': 10485760,
                    'backupCount': 8,
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


def cache_key():
    args = request.args
    key = request.path + '?' + urllib.parse.urlencode([
        (k, v) for k in sorted(args) for v in sorted(args.getlist(k))
    ])
    return key


@app.route('/', methods=['get'])
def index():
    # c1 =  db.session.query(Category).filter(Category.name == 'FOF')
    # c1.update({Category.priority: 5})
    # db.session.commit()
    # db.session.close()
    return 'index'


# 记录接口调用时间，函数同名问题
# def count_time(func):
#     route_name = func.__name__
#     def wrapper():
#         start = time.time()
#         result = func()
#         end = time.time()
#         total_time = end - start
#
#         return result
#     return wrapper

# app.logger.info( '记录 {0} 接口调用的耗时时间为：{1}'.format(route_name, total_time))

@app.route('/scheduleconfirm')
def scheduleconfirm():
    now_time = datetime.datetime.now()
    str = u'批处理调用确认，调用时间：{time}'.format(time=now_time)
    # app.logger.info(str)
    return str


# 批处理调用，导入爬取的汇率数据，工商银行

@app.route('/schedule/importexchangeratequotation/<mechanismCode>', methods=['get'])
def spiderExchangeRateQuotation(mechanismCode):  # 'ICBC'
    try:
        start = time.time()
        aa = SpiderWeb.ExchangeRateQuotationWeb(config.spiderUrls['QuotationUrl'])
        result = aa.spider()
        now_time = datetime.datetime.now()
        list_inserted = []
        for dir in result:
            quotation = ExchangeRateQuotation(currency=dir.get('currency'),
                                              spotPurchasePrice=dir.get('spotPurchasePrice'),
                                              cashPurchasePrice=dir.get('cashPurchasePrice'),
                                              spotSellingPrice=dir.get('spotSellingPrice'),
                                              cashSellingPrice=dir.get('cashSellingPrice'),
                                              issuingTime=dir.get('issuingTime'), acquisitionTime=now_time,
                                              mechanismCode=mechanismCode)
            list_inserted.append(quotation)
        db.session.add_all(list_inserted)
        db.session.commit()
        db.session.close()
        end = time.time()
        total_time = end - start
        app.logger.info('记录 importexchangeratequotation 接口调用的耗时时间为：{0}'.format(total_time))
        return 'ok'
    except Exception as e:
        app.logger.info(e)
        return 'error'


# 获取汇率数据，根据issuingTime查询
@app.route('/exchangerate/getexchangeratequotationlist', methods=['get'])
@cache.cached(timeout=60 * 60, key_prefix=cache_key)
def getexchangeratequotationlist():
    try:
        start = time.time()
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
            param.append(
                ExchangeRateQuotation.acquisitionTime >= datetime.datetime.strptime(issuingBeginTime, "%Y-%m-%d"))

        if issuingEndTime:
            # param.append(db.cast(ExchangeRateQuotation.issuingTime, db.Date) < db.cast(issuingEndTime, db.Date))
            param.append(ExchangeRateQuotation.acquisitionTime < datetime.datetime.strptime(issuingEndTime,
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
        end = time.time()
        total_time = end - start
        app.logger.info('记录 getexchangeratequotationlist 接口调用的耗时时间为：{0}'.format(total_time))
        return r.data
    except Exception as e:
        app.logger.info(e)
        return '{"data":[],"success": false}'


# 获取基金Url地址
@app.route('/funds/getfundUrl/<code>')
@cache.cached(timeout=60 * 60, key_prefix=cache_key)
def getfundUrl(code):
    fundKey = config.config[os.getenv('FLASK_CONFIG') or 'default'].fundKey
    url = 'https://mp.fofinvesting.com/wxapi/third/token?key={key}&code={code}&type=fund' \
        .format(key=fundKey, code=code)
    app.logger.info(url)
    http = urllib3.PoolManager()
    r = http.request('get', url)
    dataJson = json.loads(r.data.decode('utf-8'))

    # writeJson
    with open('getfundUrl.txt', mode='w', encoding='utf-8') as f:
        # f.write(str(dataJson))
        json.dump(dataJson, f, ensure_ascii=False)

    result = {}
    isSuccess = True
    error = ''
    if dataJson.get('status') and dataJson.get('status') == 'error':
        result['url'] = ''
        result['code'] = ''
        error = dataJson.get('message')
        isSuccess = False
    elif dataJson.get('status') and dataJson.get('status') == 'success':
        if dataJson.get('url') and dataJson.get('code'):
            if not re.search('^https', dataJson.get('url')):
                result['url'] = dataJson.get('url').replace('http', 'https')
            else:
                result['url'] = dataJson.get('url')
            result['code'] = dataJson.get('code')
    else:
        result['url'] = ''
        result['code'] = ''
        error = '第三方接口异常'
        isSuccess = False
    r = ResultDtos.NonPagedResultDto(items=[result], isEntity=False, isSuccess=isSuccess, error=error)
    return r.data


# 导入基金数据，批处理调用，
@app.route('/funds/importfunds')
def importfunds():
    start = time.time()

    dataJson = None
    http = urllib3.PoolManager()
    fundKey = config.config[os.getenv('FLASK_CONFIG') or 'default'].fundKey
    url = 'https://mp.fofinvesting.com/wxapi/third/fundlist?key={0}'.format(fundKey)
    app.logger.info(url)
    r = http.request('get', url)
    dataJson = json.loads(r.data.decode('utf-8'))
    if not dataJson:
        return '第三方接口没有数据返回'

    # readJson
    # with open('fundsJson.txt', mode='r', encoding='utf-8') as f:
    #     t = f.read()
    #     print(type(t))
    #     dataJson = json.loads(t)

    # # writeJson
    with open('fundsJson.txt', mode='w', encoding='utf-8') as f:
        # f.write(str(dataJson))
        json.dump(dataJson, f, ensure_ascii=False)

    try:
        if dataJson.get('status') and dataJson.get('status') == 'error':
            return '没有权限或接口异常'
        else:
            if dataJson.get('amount') and dataJson.get('amount') > 0:
                bulk_funds = []
                bulk_fundsnetvalue = []
                funds = dataJson.get('funds')
                now_time = datetime.datetime.now()
                fundsData = Fund.query.all()  # 基金基础表数据
                i = 0
                for f in funds:
                    i = +1
                    code = f.get('code')
                    title = f.get('title')
                    category = f.get('category')
                    annualizedRate = f.get('annualizedRate')
                    unitNav = f.get('unitNav')
                    navDate = f.get('navDate')
                    subCategory = f.get('subCategory')
                    if not subCategory:  # 二级菜单不存在，用category填充
                        subCategory = category
                    fund_list = []
                    fund = None
                    if len(fundsData) > 0:
                        # filter是懒加载，需要转换成List才能获得结果
                        fund_list = list(filter(lambda x: x.code == code and x.title == title, fundsData))

                    if len(fund_list) > 0:
                        fund = fund_list[0]
                    if not fund:  # 不存在基金基础表数据，就插入基础表和净值表记录
                        fund = Fund(code=code, title=title, category=category, subCategory=subCategory,
                                    mechanismCode='fof',
                                    # fof 况客基金code
                                    createTime=now_time)
                        db.session.add(fund)
                        fundNetValue = FundNetValue(annualizedRate=annualizedRate, unitNav=unitNav, navDate=navDate,
                                                    createTime=now_time, fund=fund)
                        bulk_fundsnetvalue.append(fundNetValue)

                    else:  # 基金表数据存在，根据每只基金最新的净值日期更新最新数据
                        Fund2 = orm.aliased(Fund)  # 定义表别名，用于子查询
                        fundId, max_navDate = db.session.query(Fund.id, FundNetValue.navDate).join(FundNetValue) \
                            .filter(FundNetValue.navDate == db.session.query(db.func.max(FundNetValue.navDate)).join(
                            Fund2).filter(db.and_(Fund2.code == Fund.code)).filter(Fund2.code == code).group_by(
                            Fund2.code)
                                    ).order_by(Fund.code).first()

                        if max_navDate and fundId:
                            str_max_navDate = max_navDate.strftime('%Y-%m-%d')
                            if navDate > str_max_navDate:
                                fundNetValue = FundNetValue(annualizedRate=annualizedRate, unitNav=unitNav,
                                                            navDate=navDate,
                                                            createTime=now_time, fundId=int(fundId))

                                bulk_fundsnetvalue.append(fundNetValue)
                            elif navDate == str_max_navDate:  # 当天重复跑时，更新补全最新的数据
                                fundNetValue = FundNetValue.query.filter(
                                    db.and_(FundNetValue.fundId == int(fundId),
                                            FundNetValue.navDate == navDate)).first()
                                fundNetValue.annualizedRate = annualizedRate
                                fundNetValue.unitNav = unitNav
                                bulk_fundsnetvalue.append(fundNetValue)
                        else:
                            fundNetValue = FundNetValue(annualizedRate=annualizedRate, unitNav=unitNav,
                                                        navDate=navDate, createTime=now_time, fundId=fund.id)
                            bulk_fundsnetvalue.append(fundNetValue)
                    if i % 1000 == 0:
                        app.logger.info('importfunds处理成功{0}条数据'.format(i))

                # 这里要提交funds的数据，bulk_fundsnetvalue才能拿到主键id
                db.session.commit()
                db.session.bulk_save_objects(bulk_fundsnetvalue, return_defaults=False)
                db.session.commit()
                db.session.close()

                end = time.time()
                total_time = end - start
                app.logger.info('记录 funds/importfunds 接口调用的耗时时间为：{0}'.format(total_time))
                return 'ok'
            else:
                return 'ok'
    except Exception as e:
        app.logger.info('importfunds的异常：' + str(e))
        db.session.close()
        return 'error'


# 获取基金数据列表
@app.route('/funds')
@cache.cached(timeout=60 * 60, key_prefix=cache_key)
def getfoudListByPaged():
    request_args_dicts = request.args.to_dict()
    pageindex = None
    pagesize = None
    # navDate = None
    keyword = None
    codes = None
    category = None
    subCategory = None
    orgcode = None  # 机构code
    '''
    基金列表接口调整 
    1.返回近3个月的有基金净值(unitNav)的基金数据(包括按大小类查询)
    2.基金如果没有净值返回null给到前端，前端会根据null处理，不能返回0
    不再根据日期查询了
    '''
    for d in request_args_dicts:  # 忽略大小写
        if 'pageindex'.lower() == d.lower():
            pageindex = request_args_dicts.get(d)
        if 'pagesize'.lower() == d.lower():
            pagesize = request_args_dicts.get(d)
        if 'keyword'.lower() == d.lower():
            keyword = request_args_dicts.get(d)
        if 'codes'.lower() == d.lower():
            codes = request_args_dicts.get(d)
        # if 'time'.lower() == d.lower():
        #     navDate = request_args_dicts.get(d)
        if 'category'.lower() == d.lower():
            category = request_args_dicts.get(d)
        if 'subCategory'.lower() == d.lower():
            subCategory = request_args_dicts.get(d)
        if 'orgcode'.lower() == d.lower():
            orgcode = request_args_dicts.get(d)

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
    # 默认查询3个月内有基金净值的数据
    limitDate = datetime.datetime.today().date() + relativedelta(months=-3)

    if keyword or codes:
        if keyword:
            keyword_title = '%' + keyword + '%'
            keyword_code = keyword.zfill(6)
            # title模糊匹配，code不满6位自动向前补全0
            params.append(db.or_(Fund.title.like(keyword_title), Fund.code == keyword_code))
        if codes:
            params.append(Fund.code.in_(codes.split(',')))
    else:
        params.append(db.cast(FundNetValue.navDate, db.Date) >= limitDate)

    if category:
        params.append(Fund.category == category)

    if subCategory:
        params.append(Fund.subCategory == subCategory)

    if orgcode:
        params.append(Fund.mechanismCode == orgcode)

    # if navDate:  # 比较日期格式，不匹配时分秒格式
    #     params.append(db.cast(FundNetValue.navDate, db.Date) == db.cast(navDate, db.Date))

    # max_navDate = db.session.query(db.func.max(FundNetValue.navDate)).filter(Fund.id == FundNetValue.fundId).filter(
    #     *params).first()
    # if max_navDate[0]:
    #     params.append(FundNetValue.navDate == max_navDate[0])

    Fund2 = orm.aliased(Fund)  # 定义表别名，用于子查询
    # 根据title和code分组后获取最新的净值日期对应的基金数据  单个查询code 2018年之前不用显示了？
    data = db.session.query(Fund, FundNetValue).join(FundNetValue) \
        .filter(FundNetValue.navDate == db.session.query(db.func.max(FundNetValue.navDate)).join(Fund2).filter(*params)
                .filter(db.and_(Fund2.code == Fund.code)) \
                .group_by(Fund2.code)  # code分组，旧的不要了
                ).order_by(Fund.code)

    totalCount = data.count()
    dataPaged = data.paginate(page=pageindex, per_page=pagesize, error_out=False).items
    items = []

    for f, fnv in dataPaged:
        dataDic = {}
        dataDic['id'] = f.id
        dataDic['code'] = f.code
        dataDic['title'] = f.title
        dataDic['category'] = f.category
        dataDic['subCategory'] = f.subCategory
        dataDic['mechanismCode'] = f.mechanismCode
        dataDic['annualizedRate'] = fnv.annualizedRate
        if not fnv.unitNav:
            dataDic['unitNav'] = 0
        else:
            dataDic['unitNav'] = fnv.unitNav
        dataDic['navDate'] = fnv.navDate
        dataDic['createTime'] = fnv.createTime
        items.append(dataDic)

    # app.logger.info(dataPaged)
    r = ResultDtos.PagedResultDto(totalCount=totalCount, items=items, isEntity=False)
    return r.data


@app.route('/funds/subCategorys')
@cache.cached(timeout=60 * 60, key_prefix=cache_key)
def getSubCategorys():
    request_args_dicts = request.args.to_dict()
    category = None  # 一级菜单name
    for d in request_args_dicts:  # 忽略大小写
        if 'category'.lower() == d.lower():
            category = request_args_dicts.get(d)
    categorys = []
    subCategorys = []
    if category:
        categoryORM = db.session.query(Category).filter(Category.name == category).one()

        subCategorys = [c.name for c in categoryORM.subCategorys]  # subCategory对象的排序定义在models中了
    else:
        categorys_tuple_list = db.session.query(Category.name).order_by(Category.priority.desc()).all()
        # 获取一级菜单的name集合
        categorys = [x[0] for x in categorys_tuple_list]
    dicts = {'categorys': categorys, 'subCategorys': subCategorys}
    r = ResultDtos.NonPagedResultDto(items=[dicts], isEntity=False)
    return r.data


@app.before_request
def before_request():
    ip = request.remote_addr
    headers = request.headers
    url = request.url
    app.logger.info("url：{0}，heards：{1}".format(url, headers))


@app.after_request
def after_request(response):
    return response


if __name__ == '__main__':
    # app.run()
    manager.run()

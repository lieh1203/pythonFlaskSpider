# encoding=utf8
from app import db


class ExchangeRateQuotation(db.Model):
    # currency, spotPurchasePrice, cashPurchasePrice, spotSellingPrice, cashSellingPrice, issuingTime，acquisitionTime mechanismCode
    # 币种 | 现汇买入价 | 现钞买入价 | 现汇卖出价 | 现钞卖出价 | 发布时间 | 采集时间 | 机构 code
    __tablename__ = "exchangeratequotation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    currency = db.Column(db.String(20))
    spotPurchasePrice = db.Column(db.DECIMAL(precision=10, scale=4))
    cashPurchasePrice = db.Column(db.DECIMAL(precision=10, scale=4))
    spotSellingPrice = db.Column(db.DECIMAL(precision=10, scale=4))
    cashSellingPrice = db.Column(db.DECIMAL(precision=10, scale=4))
    issuingTime = db.Column(db.DateTime())
    acquisitionTime = db.Column(db.DateTime())
    mechanismCode = db.Column(db.String(20))  # 工商银行 code=ICBC


class Fund(db.Model):
    __tablename__ = "funds"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20))
    title = db.Column(db.String(50))
    category = db.Column(db.String(50))
    annualizedRate = db.Column(db.DECIMAL(precision=22, scale=18))
    unitNav = db.Column(db.DECIMAL(precision=14, scale=10))
    navDate = db.Column(db.DateTime())
    subCategory = db.Column(db.String(20))
    mechanismCode = db.Column(db.String(20)) # 机构code=ICBC
    acquisitionTime = db.Column(db.DateTime())  # 抓取时间

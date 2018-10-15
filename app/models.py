# encoding=utf8
from app import db


# class User(db.Model):
#     __tablename__ = "user"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(60), nullable=False)
#     password = db.Column(db.String(120), nullable=False)


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
    acquisitionTime =db.Column(db.DateTime())
    mechanismCode=db.Column(db.String(20)) #工商银行 code=ICBC

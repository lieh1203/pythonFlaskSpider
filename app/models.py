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

    __table_args__ = (
        # exchangeratequotation表索引
        db.Index('ix_mechanismCode', 'mechanismCode'),  # 索引
        db.Index('ix_issuingTime', 'issuingTime'),  # 索引
        db.Index('ix_acquisitionTime', 'acquisitionTime'),  # 索引
    )


class Fund(db.Model):
    __tablename__ = "funds"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20))  # 基金代码，限定6位
    title = db.Column(db.String(50))  # 基金名称
    category = db.Column(db.String(50))  # 基金所属一级类别
    subCategory = db.Column(db.String(20))  # 基金所属二级类别
    mechanismCode = db.Column(db.String(20))  # 机构code=ICBC
    createTime = db.Column(db.DateTime())  # 抓取时间

    __table_args__ = (
        # Funds表索引
        db.Index('ix_code', 'code'),  # 索引
        db.Index('ix_title', 'title'),  # 索引
        db.Index('ix_category', 'category'),  # 索引
        db.Index('ix_subCategory', 'subCategory'),  # 索引
        db.Index('ix_mechanismCode', 'mechanismCode'),  # 索引
        db.Index('ix_id_code_title_mechanismCode', 'id', 'code', 'title', 'mechanismCode'),  # 联合索引
    )


# 基金净值表
class FundNetValue(db.Model):
    __tablename__ = 'fundsnetvalue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    annualizedRate = db.Column(db.DECIMAL(precision=22, scale=18))
    unitNav = db.Column(db.DECIMAL(precision=14, scale=10))
    navDate = db.Column(db.DateTime())
    createTime = db.Column(db.DateTime())  # 抓取时间
    fundId = db.Column(db.Integer, db.ForeignKey('funds.id'))  # 基金表id外键
    fund = db.relationship('Fund', backref=db.backref('fundnetvalues', cascade="all, delete,delete-orphan"))

    __table_args__ = (
        # Funds表索引
        db.Index('ix_navDate', 'navDate'),  # 索引
        db.Index('ix_id_navDate', 'id', 'navDate'),  # 索引
    )


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))  # 基金所属一级类别名称


class SubCategory(db.Model):
    __tablename__ = 'subCategorys'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))  # 基金所属二级类别名称
    categoryId = db.Column(db.Integer, db.ForeignKey('categorys.id'))  # Category外键
    category = db.relationship('Category', backref=db.backref('subCategorys'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, orm
# 导入配置文件
from config import config
import os
from app.models import ExchangeRateQuotation, Fund, FundNetValue, Category, SubCategory

db = SQLAlchemy()
app = Flask(__name__)

app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])
db.init_app(app)
app.app_context().push()
c = Category.query.all()
# print(c)
c1 = Category(name='FOF', priority=5)
c2 = Category(name='QDII', priority=3)
c3 = Category(name='保本型', priority=2)
c4 = Category(name='债券型', priority=7)
c5 = Category(name='商品型', priority=1)
c6 = Category(name='混合型', priority=6)
c7 = Category(name='股票型', priority=8)
c8 = Category(name='货币市场型', priority=4)

s1 = SubCategory(name='FOF', category=c1, priority=1)

s2 = SubCategory(name='QDII股票', category=c2, priority=4)
s3 = SubCategory(name='QDII债券', category=c2, priority=3)
s4 = SubCategory(name='QDII其他', category=c2, priority=1)
s5 = SubCategory(name='QDII混合', category=c2, priority=2)

s6 = SubCategory(name='保本型', category=c3, priority=1)

s7 = SubCategory(name='可转换债', category=c4, priority=6)
s8 = SubCategory(name='可投转债', category=c4, priority=5)
s10 = SubCategory(name='二级债基', category=c4, priority=7)
s11 = SubCategory(name='纯债', category=c4, priority=9)
s12 = SubCategory(name='债券型指数基金', category=c4, priority=3)
s13 = SubCategory(name='短期理财', category=c4, priority=4)
s14 = SubCategory(name='一级债基', category=c4, priority=8)
s15 = SubCategory(name='债券型分级基金', category=c4, priority=2)
s16 = SubCategory(name='债券型封闭基金', category=c4, priority=1)

s17 = SubCategory(name='商品型', category=c5, priority=1)

s18 = SubCategory(name='偏股型', category=c6, priority=7)
s19 = SubCategory(name='灵活配置型', category=c6, priority=5)
s20 = SubCategory(name='行业偏股型', category=c6, priority=3)
s21 = SubCategory(name='其他混合型', category=c6, priority=1)
s22 = SubCategory(name='偏债型', category=c6, priority=6)
s23 = SubCategory(name='绝对收益', category=c6, priority=2)
s24 = SubCategory(name='股债平衡型', category=c6, priority=4)
s25 = SubCategory(name='沪港深', category=c6, priority=0)

s26 = SubCategory(name='股票型指数基金', category=c7, priority=4)
s27 = SubCategory(name='股票型主动管理', category=c7, priority=5)
s28 = SubCategory(name='股票型行业基金', category=c7, priority=3)
s29 = SubCategory(name='沪港深', category=c7, priority=0)
s30 = SubCategory(name='股票型分级基金', category=c7, priority=2)
s31 = SubCategory(name='股票型封闭基金', category=c7, priority=1)

s32 = SubCategory(name='货币市场型', category=c8, priority=1)

db.session.add_all([s1, s2, s3, s4, s5, s6, s7, s8, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22,
                    s23, s24, s25, s26, s27, s28, s29, s30, s31, s32])
db.session.commit()
db.session.close()

print('ok')

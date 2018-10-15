# encoding=utf8
from sqlalchemy.orm import class_mapper
from app.models import ExchangeRateQuotation

def as_dict(obj):
    # return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    # 上面的有缺陷，表字段和属性不一致会有问题
    return dict((col.name, getattr(obj, col.name)) \
                for col in class_mapper(obj.__class__).mapped_table.c)

# ExchangeRateQuotation
# class_mapper(ExchangeRateQuotation.__class__)._orm_columns
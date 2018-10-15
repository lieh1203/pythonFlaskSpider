# encoding=utf8
from sqlalchemy.orm import class_mapper
import json

'''
       他们返回的接口格式是
    {
     data:[],
     success:true
    }
    分页的话

    {
     data:{
      rows:[],
      total:100
     },
     success:true
    }
    '''


class NonPagedResultDto(object):
    __objData = {}
    items = []
    data = ''

    def __init__(self,items=[]):
        lists = []
        for e in items:
            columns = class_mapper(e.__class__).columns
            # str(getattr(e, col.name)) 获取的值有decimal类型的，要转换成字符串
            # getattr(obj, col.name) 根据属性名称获取对象中所对应的值
            d = dict((col.name, str(getattr(e, col.name))) for col in columns)
            lists.append(d)
        #print(lists)
        if items.__len__() <= 0:
            self.items = []
        else:
            self.items = lists

        self.__objData={
            'data': self.items,
            'success': True
        }
        self.data = json.dumps(self.__objData, ensure_ascii=False)

class PagedResultDto(object):
    __objData = {}
    items = []
    totalCount = 0
    data = ''

    def __init__(self, totalCount=0, items=[]):
        lists = []
        for e in items:
            columns = class_mapper(e.__class__).columns
            # str(getattr(e, col.name)) 获取的值有decimal类型的，要转换成字符串
            # getattr(obj, col.name) 根据属性名称获取对象中所对应的值
            d = dict((col.name, str(getattr(e, col.name))) for col in columns)
            lists.append(d)
        #print(lists)
        if items.__len__() <= 0:
            self.items = []
        else:
            self.items = lists  # json.dumps(lists, ensure_ascii=False)
            self.totalCount = totalCount

        self.__objData['result'] = {
            'totalCount': self.totalCount,
            'items': self.items,
            'success': True
        }
        self.data = json.dumps(self.__objData, ensure_ascii=False)


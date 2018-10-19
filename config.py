# encoding=utf8
import  os
basedir=os.path.abspath(os.path.dirname(__file__))
#基类Config包含通用配置
class Config:
  SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to  guess string'
  #配置请求执行完逻辑之后自动提交
  SQLALCHEMY_COMMIT_ON_TEARDOWN=True
  #这个类似于主题概要的意思，但不是主题，
  # 只是在主题前面加个修饰前缀
  FLASK_MAIL_SUBJECT_PREFIX='[Flask]'
  #这个是发件人
  FLASK_MAIL_SENDER="1634217611"
  FLASK_ADMIN=os.environ.get('FLASK_ADMIN')
  #flask接口返回的内容中文乱码，设置False
  JSON_AS_ASCII = False
  fundKey='21p6cuo9reiw1x4wcsd0n769w0uow0yy'

@staticmethod
def init_app(app):
    pass
#开发环境下的配置
class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER='smtp.qq.com'
    MAIL_PORT=465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #mysql+pymysql://root:root@localhost:3306/pythondb?charset=utf8
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/pythondb?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
#测试环境下的配置
class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/testdemo'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
#生产环境下的配置
class ProductionConfig(Config): #?charset=utf8
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yida_admin:yidaAdmin2018@rdszgem56jakaheliirk2public.mysql.rds.aliyuncs.com:3306/yida-data'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True

#在config字典中注册了不同的配置环境
config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}


spiderUrls = {
    "QuotationUrl": "http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx"
}

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, orm
# 导入配置文件
from config import config
from flask_cache import Cache

# 创建扩展对象，但没有初始化
db = SQLAlchemy(session_options={'autoflush': False, 'autocommit': False})
orm = orm
cache = Cache()


# 导入蓝图
# 传入配置名，得到一个程序实例对象
def create_app(config_name):
    app = Flask(__name__)
    # 程序实例对象配置
    app.config.from_object(config[config_name])
    # 初始化各种扩展对象
    cache.init_app(app)
    db.init_app(app)
    return app

from flask import Flask
import os

app = Flask(__name__)
app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix="/admin")


key = os.urandom(24)

app.config['SECRET_KEY']= r'\x86e\x8c\xb5gy!q\xaf\x95E\xf0\xa5K\x1f\xcf\x9a\xe4^r\x85\xd7\xb3\x13'


# 服务器所在路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 注册过滤器,获取所有的标签
@app.template_filter()
def gettagsall(a):
    from app.models import Tags
    tags = Tags.query.all()
    return tags



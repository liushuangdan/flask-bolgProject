from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost/blog"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)


#会员数据模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    pwd= db.Column(db.String(100))
    email= db.Column(db.String(100))
    phone= db.Column(db.String(11),unique=True)
    status = db.Column(db.Integer,default=0)
    info= db.Column(db.Text)
    face = db.Column(db.String(255))
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    posts = db.relationship('Posts',backref="user",cascade="all, delete,delete-orphan")
    comments = db.relationship('Comments',backref="user",cascade="all, delete,delete-orphan")
    reply = db.relationship('Reply',backref="user",cascade="all, delete,delete-orphan")
    def __repr__(self):
        return '<User %r>' % self.email

    # 密码加密方法
    @classmethod
    def MD5password(cls,password):
        import hashlib
        m2 = hashlib.md5()
        m2.update(password.encode("utf-8"))
        return m2.hexdigest()


tags = db.Table('post_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)
#文章
class Posts(db.Model):
    __tablename__= 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    context = db.Column(db.Text)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tags',secondary=tags,backref='posts')
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    comments = db.relationship('Comments',backref="posts",cascade="all, delete,delete-orphan")

    def __repr__(self):
        return self.title


#标签
class Tags(db.Model):
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    
    def __repr__(self):
        return self.name


# 评论
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    context = db.Column(db.String(255))
    status = db.Column(db.Integer)
    reply =  db.relationship('Reply',backref="comments",cascade="all, delete,delete-orphan")


# 回复模型
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid =  db.Column(db.Integer, db.ForeignKey('comments.id'))
    context = db.Column(db.String(255))
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    rid = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


manager.add_command('db', MigrateCommand)
if __name__=='__main__':
    # db.create_all()
    manager.run()

    
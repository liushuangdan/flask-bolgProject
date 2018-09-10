from . import home
from flask import render_template,url_for,request,session,jsonify
from app.models import *
import os,json,time,random,re
import copy

# 请求处理之前的 装饰器
@home.before_request
def checklogin():
    # 获取当前的请求路径
    path = request.path
    # 要求登录才能请求的路径
    urllist = [url_for('home.createblog'),url_for('home.comment'),url_for('home.hf')]
    if path in urllist:
        # 判断是否登录
        if not session.get('VipUser',None):
                return '<script>alert("请先登录");location.href="'+url_for('home.login')+'?next='+path+'"</script>'

#注册 
@home.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'GET':

        return render_template('home/lw-re.html')

    elif request.method == 'POST':
        try:
            #接收数据
            data = {}
            data['name'] = request.values['name']
            data['email'] = request.values['email']
            data['pwd'] = User.MD5password(request.values['pwd'])
            data['phone'] = request.values['phone']
            #入库
            ob = User(**data)
            db.session.add(ob)
            db.session.commit()

            res = """<script>alert("注册成功,请登录");location.href='{url}'</script>
            """.format(url=url_for('home.login'))
        except:
            res = """<script>alert("注册失败,请重新注册");location.href='{url}'</script>
            """.format(url=url_for('home.register'))

        return res
        


# 发送短信验证码
@home.route('/sendSMS',methods=['POST','GET'])
def sendSMS():
    # 接受手机号
    phone = request.values.get('phone')

    # 生成验证码
    code = random.randint(11111,99999)
    # 存储到session中
    session['code'] = code

    print(code)

    # 调用方法 发送短信验证
    from app.static.dysms import demo_sms_send

    res = demo_sms_send.send(code,phone)
    # if res['Code'] == 'OK':
    #         # 发送成功
    #         return True
    #     else:
    #         # 发送失败
    #         print(res)
    #         return False

    return res

    # print(res)
    # # {
    # #   "Message":"OK",
    # #   "RequestId":"A44C3901-96BA-4D82-BE06-E5FEF11DA3E7",
    # #   "BizId":"405025435097521530^0",
    # #   "Code":"OK"
    # #  }


#登录
@home.route('/login',methods=['POST','GET'])
def login():
    nextpath = request.args.get('next','/')
    if request.method == 'GET':
        return render_template('home/lw-log.html')

    elif request.method == 'POST':
        email = request.values['email']
        password = User.MD5password(request.values['pwd']) 
        #查数据
        ob = User.query.filter_by(email=email).first()
        
        if ob != None:
            if ob.pwd == password:
                # 密码正确
                # 执行登录
                session['VipUser'] = {'uid':ob.id,'email':ob.email,'username':ob.name}

                print(session['VipUser'])
                res = '<script>alert("登录成功");location.href="'+nextpath+'"</script>'
            else:

                res = '<script>alert("用户名或密码错误!请重新登录");history.back(-1)</script>'
            
        else:

            res = '<script>alert("用户名或密码错误!请重新登录");history.back(-1)</script>'

        return res



#退出登录
@home.route('/logout')
def logout():

    session.pop('VipUser')

    return "<script>alert('退出成功');location.href='/'</script>"

#个人中心
@home.route('/member',methods=['POST','GET'])
def member():
    uid = session['VipUser']['uid']
    # print(uid)
    #查找用户
    user = User.query.filter_by(id=session['VipUser']['uid']).first()
    #查找用户名下所有的博文
    ps = user.posts
    # print(ps)
    #准备数据
    
    data={'ps':ps,'user':user}

    return render_template('/home/member.html',ps=data)

#个人中心的编辑
@home.route('/edit',methods=['POST','GET'])
def edit():
    uid = session['VipUser']['uid']
    # print(uid)
    #查找用户
    user = User.query.filter_by(id=session['VipUser']['uid']).first()
    #查找用户名下所有的博文
    ps = user.posts
    # print(ps)
    #准备数据
    
    data={'ps':ps,'user':user}

    return render_template('/home/memberedit.html',ps=data)


#个人中心的修改
@home.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'GET':

        return render_template('/home/member.html')

    elif request.method == 'POST':
        try:
            #接收数据
            uid = request.values['uid']
            # print(uid)
            #查找用户的信息
            user = User.query.get(request.values['uid'])
            # print(user)

            user.name = request.values['name']
            user.email = request.values['email']
            user.pwd = User.MD5password(request.values['pwd'])
            user.phone = request.values['phone']
            user.info = request.values['info']

            myfile = request.files['face']

            from app import BASE_DIR
            # 检测是否有上传文件
            if myfile:
                try:
                    os.remove(BASE_DIR + user.face)
                except:
                    pass

                Suffix = myfile.filename.split('.').pop()
                filename = str(time.time())+str(random.randint(10000,99999))+'.'+Suffix
                imgurl = '/static/uploads/'+filename
                myfile.save(BASE_DIR + imgurl)

                user.face = imgurl

                # user.face = request.values['face']

            #入库
            db.session.add(user)
            db.session.commit()

            res = """<script>alert("博主信息修改成功");location.href='{url}'</script>
            """.format(url=url_for('home.member'))
        except:
            res = """<script>alert("博主信息修改失败);location.href='{url}'</script>
            """.format(url=url_for('home.member'))

        return res


# 博文发布
@home.route('/create/blog/',methods=['GET','POST'])
def createblog():
    if request.method == 'GET':
        # 获取所有的标签
        tags = Tags.query.all()
        # 返回一个博文发布页面
        return render_template('/home/blogs/add.html',tags=tags)

    elif request.method == 'POST':
        # 执行博文的添加

        # 准备数据
        data = {}
        data['title'] = request.form.get('title')
        data['uid'] = session['VipUser']['uid']
        data['context'] = request.form.get('content')
        
        # 创建文章
        post = Posts(**data)
        # 给文章设置标签
        post.tags = list(map(lambda x:Tags.query.get(x),request.form.getlist('tags')))
        # 执行添加
        db.session.add(post)
        db.session.commit()

        # return '发布成功'
        return '<script>alert("发布成功");location.href="'+url_for('home.bloginfo',post_id=post.id)+'"</script>'


#博文详情
@home.route('/bloginfo/<int:post_id>')
def bloginfo(post_id):
    
    # 取文章内容
    info = Posts.query.get(post_id)
    tags = info.tags
    # 查找评论信息
    comments = Comments.query.filter_by(posts_id=post_id).all()

    data={'info':info,'tags':tags,'comments':comments}
    
    return render_template('home/blogs/bloginfo.html',info=data)


# 搜索按照标题
@home.route('/search')
def search():
    #获取要搜索的内容
    info = request.values['keywords']
    print(info)
    # 根据关键字去库里查
    title = Posts.query.filter(Posts.title.contains(info)).all()
    print(title)
    # 根据用户名查
    users = User.query.filter(User.name.contains(info)).all()

    data = {'title':title,'users':users}

    return render_template('/home/blogs/search.html',data=data)



# 博文列表 按用户
@home.route('/userblogs/<int:id>')
def userblogs(id):

    user=User.query.get(id)
    ps = user.posts
    data = {'ps':ps,'user':user}

    return render_template('home/blogs/userlist.html',ps=data)


# 博文列表 按标签
@home.route('/blogs/tags/<int:tid>/')
def tagsblogs(tid):

    # 根据标签id获取标签
    tag = Tags.query.get(tid)
    ps = tag.posts

    return render_template('/home/blogs/taglist.html',ps=ps)


# 评论
@home.route('/comment',methods=["post"])
def comment():
    data={}
    data['context'] = request.values['context']
    data['posts_id'] = request.values['pid']
    data['user_id'] = session['VipUser']['uid']

    ob = Comments(**data)
    db.session.add(ob)
    db.session.commit()

    res = """<script>alert("评论成功");location.href='{url}'</script>
            """.format(url=url_for('home.bloginfo',post_id=request.values['pid']))

    return res

# 回复
@home.route('/hf',methods=["POST"])
def hf():
    # 获取回复的信息
    data = {}
    data['cid'] = request.values['cid']
    data['context'] = request.values['context']
    data['user_id'] = session['VipUser']['uid']
    try:
        data['rid'] = request.values['rid']
    except:
        pass

    # 评论
    r = Comments.query.get(request.values['cid'])
    pid = r.posts_id

    ob = Reply(**data)
    db.session.add(ob)
    db.session.commit()
    res = "<script>alert('回复成功');location.href='{}'</script> ".format(url_for('home.bloginfo',post_id=pid))
    return res


# ueditor读取配置文件
@home.route('/ueditconfig/', methods=['GET', 'POST'])
def ueditconfig():
    # 导入地址
    from app import BASE_DIR
    # 获取请求动作
    action = request.args.get('action')
    result = {}
    # 读取配置文件
    if action == 'config':
    # 初始化时，返回配置文件给客户端
        with open(os.path.join(BASE_DIR,'static', 'ueditor', 'php',
                               'config.json')) as fp:
            try:
                # 删除 `/**/` 之间的注释
                CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
            except:
                CONFIG = {}
        result = CONFIG
    # 文件上传
    if action  == 'uploadimage':
        upfile = request.files['upfile']  # 这个表单名称以配置文件为准
        # upfile 为 FileStorage 对象
        # 这里保存文件并返回相应的URL

        Suffix = upfile.filename.split('.').pop()
        filename = str(time.time())+str(random.randint(10000,99999))+'.'+Suffix
        imgurl = '/static/uploads/'+filename
        upfile.save(BASE_DIR+imgurl)

        result = {
            "state": "SUCCESS",
            "url": imgurl,
            "title": filename,
            "original":filename
        }

        print(BASE_DIR)

    return json.dumps(result)


#首页
@home.route('/')
def home():

    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取所有的博文 参数1 当前页码数  参数2 每页显示的数量
    ps =Posts.query.filter().paginate(p,3)

    a = list(ps.iter_pages())
    b = len(a)
    # print(b)
    data ={'ps':ps,'b':b}

    return render_template('/home/index.html',**data)




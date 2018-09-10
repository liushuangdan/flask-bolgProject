from . import admin
from app.models import *
from flask import render_template,request,jsonify,url_for,session

@admin.route("/")
def index():

    # 统计 用户,博文,评论,标签 数量
    data = {}
    data['usnum'] = User.query.filter().count()
    data['bsnum'] = Posts.query.filter().count()
    data['csnum'] = Comments.query.filter().count()
    data['tsnum'] = Tags.query.filter().count()
    data['rsnum'] = Reply.query.filter().count()

    return render_template('/admin/admin.html',**data)

# 用户列表
@admin.route('/user/list/')
def userlist():
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取用户数据  参数1 当前页码数  参数2 每页显示的数量
    users = User.query.filter().paginate(p,1)

    a = list(users.iter_pages())
    b = len(a)
    # print(b)
    data ={'users':users,'b':b}

    return render_template('/admin/user/userlist.html',**data)

#博文搜索
@admin.route('/user/search/',methods=['POST','GET'])
def user_search():
    p = int(request.args.get('p',1))
    try:
        keywords = request.values['keywords']

        users = User.query.filter(User.name.contains(keywords)).paginate(p,3)

    except:
        users = User.query.filter().paginate(p,3)

    a = list(users.iter_pages())
    b = len(a)
    # print(b)
    data ={'users':users,'b':b}

    return render_template('/admin/user/userlist.html',**data)

# 用户状态的修改
@admin.route('/user/statusedit/')
def useredit():
    try:
        #获取用户对象
        ob = User.query.get(request.args.get('uid'))
        # 更新状态
        ob.status = int(request.args.get('status')) 
        # 执行
        db.session.add(ob)
        db.session.commit()
        res = {'error':1,'msg':'修改状态成功'}
    except:
        res = {'error':0,'msg':'修改状态失败'}

    return jsonify(res)

# 用户的删除
@admin.route('/user/delete/')
def userdelete():
    try:
        postdelete
        #获取用户对象
        ob = User.query.get(request.args.get('uid'))
        # 执行
        db.session.delete(ob)
        db.session.commit()

        data = {'error':1,'msg':'用户删除成功'}
    except:
        data = {'error':0,'msg':'用户删除失败'}

    return jsonify(data)


# 博文列表
@admin.route('/blogs/list/')
def blogslist():
    #遍历所有的博文
    # ps = Posts.query.all()
    # print(ps)
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取用户数据  参数1 当前页码数  参数2 每页显示的数量
    ps = Posts.query.filter().paginate(p,3)

    a = list(ps.iter_pages())
    b = len(a)
    # print(b)
    data ={'ps':ps,'b':b}

    return render_template('/admin/bloglist.html',**data)


#博文搜索
@admin.route('/blogs/search/',methods=['POST','GET'])
def blogs_search():
    p = int(request.args.get('p',1))
    try:
        keywords = request.values['keywords']

        ps = Posts.query.filter(Posts.title.contains(keywords)).paginate(p,3)
    except:
        ps = Posts.query.filter().paginate(p,3)

    a = list(ps.iter_pages())
    b = len(a)
    # print(b)
    data ={'ps':ps,'b':b}

    return render_template('/admin/bloglist.html',**data)




# 博文的删除
@admin.route('/post/delete/')
def postdelete():
    try:
        #获取用户对象
        ob = Posts.query.get(request.args.get('pid'))
        # 执行
        db.session.delete(ob)
        db.session.commit()

        data = {'error':1,'msg':'博文删除成功'}
    except:
        data = {'error':0,'msg':'博文删除失败'}

    return jsonify(data)


# 标签列表
@admin.route('/tags/list/')
def tagslist():
    #遍历所有的标签
    # ts = Tags.query.filter().all()

    # print(ts)
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取用户数据  参数1 当前页码数  参数2 每页显示的数量
    ts = Tags.query.filter().paginate(p,3)

    a = list(ts.iter_pages())
    b = len(a)
    # print(b)
    data ={'ts':ts,'b':b}

    return render_template('/admin/tagslist.html',**data)


#标签搜索
@admin.route('/tags/search/',methods=['POST','GET'])
def tags_search():
    p = int(request.args.get('p',1))
    try:
        keywords = request.values['keywords']
        ts = Tags.query.filter(Tags.name.contains(keywords)).paginate(p,3)
    except:
        ts = Tags.query.filter().paginate(p,3)

    a = list(ts.iter_pages())
    b = len(a)
    # print(b)
    data ={'ts':ts,'b':b}


    return render_template('/admin/tagslist.html',**data)



# 标签的删除
@admin.route('/tag/delete/')
def tagdelete():
    try:
        #获取用户对象
        ob = Tags.query.get(request.args.get('tid'))
        # 执行
        db.session.delete(ob)
        db.session.commit()

        data = {'error':1,'msg':'标签删除成功'}
    except:
        data = {'error':0,'msg':'标签删除失败'}

    return jsonify(data)


#标签的添加
@admin.route('/tag/add/',methods=['POST','GET'])
def tagadd():

    t = Tags()
    t.name = request.values['name']
    db.session.add(t)
    db.session.commit()

    return '<script>alert("标签添加成功");location.href="'+url_for('admin.tagslist')+'"</script>'

#标签的更新
@admin.route('/tag/update/',methods=['POST','GET'])
def tagupdate():
    try:
        #获取标签对象
        ob = Tags.query.get(request.args.get('tid'))
        # 更新状态
        ob.name = request.values['name']
        # 执行
        db.session.add(ob)
        db.session.commit()
        data = {'error':1,'msg':'修改标签成功'}
    except:
        data = {'error':0,'msg':'修改标签失败'}

    return jsonify(data)


# 评论列表
@admin.route('/comments/list/')
def commentslist():
    # co = Comments.query.filter().all()

    # 获取页码数
    p = int(request.args.get('p',1))

    # 获取用户数据  参数1 当前页码数  参数2 每页显示的数量

    co = Comments.query.filter().paginate(p,3)

    a = list(co.iter_pages())
    b = len(a)
    # print(b)
    data ={'co':co,'b':b}

    return render_template('/admin/commentslist.html',**data)

#评论搜索
@admin.route('/comments/search/',methods=['POST','GET'])
def comments_search():
    p = int(request.args.get('p',1))
    try:
        keywords = request.values['keywords']
        co = Comments.query.filter(Comments.context.contains(keywords)).paginate(p,3)
    except:
        co = Comments.query.filter().paginate(p,3)

    a = list(co.iter_pages())
    b = len(a)
    # print(b)
    data ={'co':co,'b':b}

    return render_template('/admin/commentslist.html',**data)


# 标签的删除
@admin.route('/com/delete/')
def comdelete():
    try:
        #获取用户对象
        ob = Comments.query.get(request.args.get('cid'))
        # 执行
        db.session.delete(ob)
        db.session.commit()

        data = {'error':1,'msg':'评论删除成功'}
    except:
        data = {'error':0,'msg':'评论删除失败'}

    return jsonify(data)


# 请求处理之前的 装饰器
@admin.before_request
def checklogin():
    # 获取当前的请求路径
    path = request.path
    # 要求登录才能请求的路径
    urllist = [url_for('admin.userlist'),url_for('admin.blogslist'),url_for('admin.commentslist'),url_for('admin.index')]
    if path in urllist:
        # 判断是否登录
        if not session.get('User',None):

                return '<script>alert("请先登录");location.href="'+url_for('admin.login')+'?next='+path+'"</script>'


#登录
@admin.route('/login',methods=['POST','GET'])
def login():
    nextpath = request.args.get('next','/admin')
    if request.method == 'GET':
        return render_template('admin/login.html')

    elif request.method == 'POST':
        
        if  request.values['email']=='123@qq.com' and request.values['pwd']== '123456' :
            email=request.values['email']
            pwd = request.values['pwd'] 

            session['User'] = {'email':email}

            res = '<script>alert("登录成功");location.href="'+nextpath+'"</script>'
            
        else:
            res = '<script>alert("用户名或密码错误!请重新登录");location.href="'+nextpath+'"</script>'


        return res


#退出登录
@admin.route('/logout')
def logout():
    session.pop('User')

    return "<script>alert('退出成功');location.href='"+url_for('admin.login')+"'</script>"








import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
# 设置SQLite数据库URI
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# 每次请求提交后，自动提交数据库的修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '577024128@qq.com'
app.config['FLASKY_ADMIN'] = '577024128@qq.com'
app.config['MAIL_DEBUG'] = True             # 开启debug，便于调试看信息
app.config['MAIL_SUPPRESS_SEND'] = False    # 发送邮件，为True则不发送
app.config['MAIL_SERVER'] = 'smtp.qq.com'   # 邮箱服务器
app.config['MAIL_PORT'] = 465               # 端口
app.config['MAIL_USE_SSL'] = True           # 重要，qq邮箱需要使用SSL
app.config['MAIL_USE_TLS'] = False          # 不需要使用TLS
app.config['MAIL_USERNAME'] = '577024128@qq.com'  # 填邮箱
<<<<<<< HEAD
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')      # 填授权码
=======
app.config['MAIL_PASSWORD'] = 'qraqnoimfnuxbbhg'      # 填授权码
>>>>>>> origin/master

bootstrap = Bootstrap(app)
moment = Moment(app)
# 获取数据库对象
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):

    """database table class Role """
    # 表名，一般采用 复数 形式
    __tablename__ = 'roles'
    # 类变量即数据表的字段，由 db.Column创建
    # primary_key = True 定义主键
    # unique = True 不允许出现重复的值
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # backref 反向引用：像User模型（类）添加role参数（属性）
    # 添加到 Role 中的 users 属性代表了关系的面向对象视角，
    # 将返回与角色相关联的用户的列表，第一个参数 用字符串表示关系另一端的模型
    # 通过User实例的这个属性可以获取对应的Role模型对象，而不用再通过role_id外键获取
    # lazy='dynamic'禁止自动执行查询
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 返回表示模型的字符串，供调试和测试使用
    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    """database table class User"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 创建外链，与roles.id这个外键建立关系（roles.id:表roles的id字段）
    # role_id 返回的是外键的值
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


class NameForm(FlaskForm):
    name = StringField('请输入你的名字?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# 添加一个shell上下文
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))

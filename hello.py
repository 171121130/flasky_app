import os
from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))#获得当前文件路径
#数据库 URL 必须保存到 Flask 配置对象的 SQLALCHEMY_DATABASE_URI 键中
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#SQLALCHEMY_COMMIT_ON_TEARDOWN 键，将其设为 True时，每次请求结束后都会自动提交数据库中的变动
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)#unique不重复
    users = db.relationship('User', backref='role', lazy='dynamic')# backref 参数向 User 模型中添加一个 role 属性

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])#
    password = StringField('What is your password?', validators=[Required()])
    submit = SubmitField('Submit')


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
        user = User.query.filter_by(username=form.name.data).first()  # 查询User类中是否重复
        if user is None:  # 不重复
            user = User(username=form.name.data)  # 传入User类的username
            db.session.add(user)  # 数据库表单添加行
            session['known'] = False  # 变量 known 被写入用户会话中,可以传给html
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))  # 重定向到index()
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))  # 渲染html


if __name__ == '__main__':
    manager.run()

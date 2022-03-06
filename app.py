from flask import Flask
from flask import render_template,request,redirect,abort
from flask import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from flask_login import UserMixin , LoginManager , login_user , logout_user , login_required
import os
from werkzeug.security import generate_password_hash,check_password_hash

#インスタンス化
app = Flask(__name__)

#SQLalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

#loginmanagerのインスタンス化
login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    #id
    id = db.Column(db.Integer, primary_key=True)
    #タイトル
    title = db.Column(db.String(50), nullable=False)
    #本文
    body = db.Column(db.String(300), nullable=False)
    #投稿日時
    default = datetime.now(pytz.timezone("Asia/Tokyo"))
    created_at = db.Column(db.DateTime, nullable=False, default = default.replace(microsecond=0))

class User(UserMixin,db.Model):
    #id
    id = db.Column(db.Integer, primary_key=True)
    #ユーザ名
    user_name = db.Column(db.String(30),unique=True)
    #パスワード
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#各ページのルーティング
#ルートページ
@app.route("/index",methods=['GET','POST'])
@login_required #loginしていないとアクセス拒否
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template("index.html",posts=posts)

#サインアップ
@app.route('/signup',methods=['GET','POST'])
def signup():
    #POST通信 or GET通信
    if request.method == 'POST':#フォームに入力がある場合（post）
        user_name = request.form.get('user_name')
        password = request.form.get('password') 
        
        #passwordはハッシュ化
        user = User(user_name=user_name , password=generate_password_hash(password,method='sha256'))
        
        #DBへの追加
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:  #入力がなければ(get)もう一度signupへ
        return render_template('signup.html')

#ログイン
@app.route('/',methods=['GET','POST'])
def login():
    #POST通信 or GET通信
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password') 
        
        #Userテーブルからuser_nameに合致するものを取得
        user = User.query.filter_by(user_name=user_name).first()
        
        #user.password（ハッシュ化したパスワード）と入力されたパスワードのチェック
        if check_password_hash(user.password,password):
            login_user(user)
            return redirect('/index') #('/')
        else:
            return abort(401)
    
    else:      
        return render_template('login.html')

@app.route('/logout')
@login_required #loginしていないとアクセス拒否
def logout():
    logout_user()
    return redirect('/')
    
#投稿ページ
@app.route('/create',methods=['GET','POST'])
@login_required 
def create():
    #POST通信 or GET通信
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')     
        
        post = Post(title=title , body=body)
        #DBへの追加
        db.session.add(post)
        db.session.commit()
        return redirect('/index')
    else:      
        return render_template('create.html')

#編集ページ
@app.route('/<int:id>/update',methods=['GET','POST'])
@login_required 
def update(id):
    post = Post.query.get(id)
    
    #POST通信 or GET通信
    if request.method == 'POST':
        #上書き
        post.title = request.form.get('title')
        post.body = request.form.get('body')     

        #DBの更新
        db.session.commit()
        return redirect('/index')
    
    else:      
        return render_template('update.html',post=post)
    
#削除
@app.route('/<int:id>/delete',methods=['GET'])
@login_required 
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect('/index')

if __name__ == "__main__":
    app.debug=True
    app.run()
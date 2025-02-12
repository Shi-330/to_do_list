import os
import json
from datetime import datetime
#flask
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
#google api
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

app = Flask(__name__)
# データベースの設定

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLAlchemyの初期化
db = SQLAlchemy(app)
# ログインマネージャーの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# OAuth2設定ファイル
# CLIENT_SECRET_FILE = 'credentials.json'  # ここにダウンロードしたJSONファイル名を指定
# SCOPES = ['https://www.googleapis.com/auth/calendar']


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

# タスクモデルの定義
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # タスクタイトル
    description = db.Column(db.String(200))  # タスクの詳細
    ddl_date = db.Column(db.DateTime)  # 締切日
    credit = db.Column(db.Integer)
    preference = db.Column(db.Integer)
    status = db.Column(db.String(20), default='未完成')  # タスクの状態（デフォルトは「未完成」）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

    def formatted_ddl(self):
        if self.ddl_date:
            return self.ddl_date.strftime('%Y-%m-%d')
        return '未设置'
    
# データベースの作成
with app.app_context():
    db.create_all()

# def get_calendar_service():
#     """Google Calendar API サービスオブジェクトを作成"""
#     creds = None
#     # OAuth 2.0 認証フロー
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)

#         # トークンを保存
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     # Google Calendar APIサービスの構築
#     service = build('calendar', 'v3', credentials=creds)
#     return service

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
@login_required
def index():
    sort_by = request.args.get('sort_by', 'ddl_date')  # 
    sort_order = request.args.get('sort_order', 'asc')  # 

    if sort_by == 'ddl_date':
        sort_column = Task.ddl_date
    elif sort_by == 'credit':
        sort_column = Task.credit
    elif sort_by == 'preference':
        sort_column = Task.preference
    else:
        sort_column = Task.ddl_date

    if sort_order == 'asc':
        tasks = Task.query.order_by(sort_column.asc()).all()
    else:
        tasks = Task.query.order_by(sort_column.desc()).all()

    return render_template('index.html', tasks=tasks, sort_by=sort_by, sort_order=sort_order)

# 新しいタスクを追加する処理
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    ddl_date = datetime.strptime(request.form.get('ddl_date'), '%Y-%m-%d')
    credit = request.form.get('credit')
    preference = request.form.get('preference')
    
    new_task = Task(
        title=title,
        description=description,
        ddl_date=ddl_date,
        credit=credit,
        preference=preference,
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You are not authorized to delete this task.')
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You are not authorized to update this task.')
        return redirect(url_for('index'))
    task.status = '完了'
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password) 
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# # カレンダーイベント追加
# @app.route('/sync_calendar', methods=['POST'])
# @login_required
# def sync_calendar():
#     # ユーザーの課題データをすべて取得
#     tasks = Task.query.filter_by(user_id=current_user.id).all()

#     if not tasks:
#         flash("登録された課題がありません。")
#         return redirect(url_for('index'))

#     # Googleカレンダーにイベントを追加する
#     service = get_calendar_service()
#     for task in tasks:
#         due_date = datetime.datetime.now() + datetime.timedelta(days=7)  # 締め切り情報を追加する場合は変更

#         event = {
#             'summary': task.title,
#             'description': task.description,
#             'start': {
#                 'dateTime': due_date.isoformat(),
#                 'timeZone': 'Asia/Tokyo',
#             },
#             'end': {
#                 'dateTime': (due_date + datetime.timedelta(hours=1)).isoformat(),
#                 'timeZone': 'Asia/Tokyo',
#             },
#         }

#         service.events().insert(calendarId='primary', body=event).execute()

#     flash(f'{len(tasks)}件の課題がGoogleカレンダーに登録されました。')
#     return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)


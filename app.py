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
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


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
# OAuth2設定ファイル
CLIENT_SECRET_FILE = 'credentials.json'  # ここにダウンロードしたJSONファイル名を指定
SCOPES = ['https://www.googleapis.com/auth/tasks']

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

    importance = db.Column(db.Float, default=0.0)  # 重要度
    urgency = db.Column(db.Float, default=0.0)    # 紧急度

    deleted_flag = db.Column(db.Boolean, default=False)  # 削除フラグを追加
    google_task_id = db.Column(db.String(50), nullable=True,default='')  # Google TasksのIDフィールド


    status = db.Column(db.String(20), default='未完成')  # タスクの状態（デフォルトは「未完成」）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

    def formatted_ddl(self):
        if self.ddl_date:
            return self.ddl_date.strftime('%Y-%m-%d')
        return '未设置'
    
    def update_priority(self):
        """自动更新优先级算法"""
        # 时间紧迫性计算（剩余天数越少，紧急度越高）
        days_left = (self.ddl_date - datetime.now()).days
        time_factor = 1 / (days_left + 1)  # +1防止除零错误
        
        # 学分重要性计算（1-10分制）
        credit_factor = self.credit / 10
        
        # 个人偏好计算（1-5分制）
        preference_factor = self.preference / 5
        
        # 组合计算（可调整权重）
        self.urgency = min(1.0, max(0.0, 
            0.6 * time_factor + 
            0.2 * credit_factor + 
            0.2 * preference_factor
        ))
        
        self.importance = min(1.0, max(0.0,
            0.7 * credit_factor +
            0.3 * preference_factor
        ))

def get_tasks_service():
    """Google Tasks API サービスオブジェクトを作成"""
    creds = None
    # OAuth 2.0 認証フロー
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri='http://localhost')
            creds = flow.run_local_server(port=0)

        # トークンを保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Google Calendar APIサービスの構築
    service = build('tasks', 'v1', credentials=creds)
    return service

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

    # 削除フラグを立てる
    task.deleted_flag = True
    db.session.commit()
    flash('タスクが削除フラグ付きで保留されました。同期時にGoogle Tasksから削除します。')
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

@app.route('/smart_view')
@login_required
def smart_view():
    # 获取当前用户的所有任务
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    # 初始化四象限字典
    quadrants = {
        'q1': [],  # 重要且紧急（Importance > 0.5, Urgency > 0.5）
        'q2': [],  # 重要不紧急（Importance > 0.5, Urgency <= 0.5）
        'q3': [],  # 紧急不重要（Importance <= 0.5, Urgency > 0.5）
        'q4': []   # 不重要不紧急（Importance <= 0.5, Urgency <= 0.5）
    }

    # 智能分类逻辑
    for task in tasks:
        # 自动计算优先级（如果未手动设置）
        if task.importance == 0 or task.urgency == 0:
            # 使用算法自动计算
            days_left = (task.ddl_date - datetime.now()).days + 1
            task.urgency = min(1.0, max(0.0, 0.4 * (1 / days_left) + 0.3 * (task.credit/10) + 0.3 * (task.preference/5)))
            task.importance = min(1.0, max(0.0, 0.5 * (task.credit/10) + 0.5 * (task.preference/5)))
            db.session.commit()

        # 进行分类
        if task.importance > 0.5:
            if task.urgency > 0.5:
                quadrants['q1'].append(task)
            else:
                quadrants['q2'].append(task)
        else:
            if task.urgency > 0.5:
                quadrants['q3'].append(task)
            else:
                quadrants['q4'].append(task)

    # 为每个象限添加排序逻辑
    quadrants['q1'].sort(key=lambda x: (-x.urgency, -x.importance))
    quadrants['q2'].sort(key=lambda x: (-x.importance, x.urgency))
    quadrants['q3'].sort(key=lambda x: (-x.urgency, x.importance))
    quadrants['q4'].sort(key=lambda x: (x.ddl_date))

    return render_template('smart_view.html', quadrants=quadrants)

@app.route("/register", methods=['GET', 'POST'])
def register():
    # 如果用户已经登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('このユーザー名は既に使用されています。', 'danger')
            return render_template('register.html', title='新規登録', form=form)
        
        try:
            # 创建新用户
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('アカウントが作成されました。ログインしてください。', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('アカウントの作成中にエラーが発生しました。', 'danger')
            app.logger.error(f"Error during registration: {str(e)}")
            
    return render_template('register.html', title='新規登録', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # 如果用户已经登录，直接重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                # 登录用户
                login_user(user)
                
                # 获取下一页地址
                next_page = request.args.get('next')
                # 安全检查：确保 next_page 是相对路径
                if next_page and not next_page.startswith('/'):
                    next_page = None
                    
                flash(f'ようこそ、{user.username}さん！', 'success')
                return redirect(next_page or url_for('index'))
            else:
                flash('ログインに失敗しました。ユーザー名とパスワードを確認してください。', 'danger')
        except Exception as e:
            flash('ログイン処理中にエラーが発生しました。', 'danger')
            app.logger.error(f"Error during login: {str(e)}")
    
    return render_template('login.html', title='ログイン', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# カレンダーイベント追加
@app.route('/sync_calendar', methods=['POST'])
@login_required
def sync_calendar():
    # ToDoリストにタスクリストを追加する
    service = get_tasks_service()
    results = service.tasks().list(tasklist='@default').execute()
    google_tasks = results.get('items', [])
    
    # Google側の既存タスク情報をタイトルと説明でセット化
    google_task_map = {task.get('title', ''): task['id'] for task in google_tasks if 'id' in task}

    # ユーザーの課題データをすべて取得
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    

    if not tasks:
        flash("登録された課題がありません。")
        return redirect(url_for('index'))

    for task in tasks:
        if task.deleted_flag:
            if task.google_task_id:
                service.tasks().delete(tasklist='@default', task=task.google_task_id).execute()
                print(f"Google Tasksからタスクを削除しました: {task.title}")
            db.session.delete(task)
            print(f"DBからタスクを削除しました: {task.title}")
        
        else:
            # google_task_idが一致する場合はスキップ
            if task.google_task_id:
                print(f"既存タスクのためスキップ: {task.title}")
                continue
            
            task_status = "completed" if task.status == "完了" else "needsAction"

            # 新規タスクとしてGoogle Tasksに登録
            task_googleTasks = {
                "status": task_status,
                "kind": "tasks#task",
                "title": task.title,
                "deleted": False,
                "due": task.ddl_date.isoformat() + 'Z' if task.ddl_date else None,
                "notes": task.description
            }

            result = service.tasks().insert(tasklist='@default', body=task_googleTasks).execute()
            google_task_id = result.get('id')  # Google Tasks IDを取得
            task.google_task_id = google_task_id
            print(f"タスクがGoogle Tasksに追加されました: {result.get('title')}")

    db.session.commit()
    flash(f'{len(tasks)}件の課題がToDoリストに登録されました。')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)


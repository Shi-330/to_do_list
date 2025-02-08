from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# データベースの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyの初期化
db = SQLAlchemy(app)

# タスクモデルの定義
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # タスクタイトル
    description = db.Column(db.String(200))  # タスクの詳細
    ddl_date = db.Column(db.DateTime)  # 締切日
    credit = db.Column(db.Integer)
    preference = db.Column(db.Integer)
    status = db.Column(db.String(20), default='未完成')  # タスクの状態（デフォルトは「未完成」）

    def __repr__(self):
        return f'<Task {self.title}>'

    def formatted_ddl(self):
        if self.ddl_date:
            return self.ddl_date.strftime('%Y-%m-%d')
        return '未设置'

# アプリケーション起動時にデータベースを作成
with app.app_context():
    db.create_all()

# ホームページ（タスク一覧）を表示
@app.route('/')
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
        preference=preference
    )
    db.session.add(new_task)
    db.session.commit()
    
    return redirect(url_for('index'))

# タスクを削除する処理
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# タスクを完了にする処理
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.status = '完了'
    db.session.commit()
    return redirect(url_for('index'))

# アプリケーションの実行
if __name__ == '__main__':
    app.run(debug=True)

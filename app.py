from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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
    status = db.Column(db.String(20), default='未完成')  # タスクの状態（デフォルトは「未完成」）

    def __repr__(self):
        return f'<Task {self.title}>'

# アプリケーション起動時にデータベースを作成
with app.app_context():
    db.create_all()

# ホームページ（タスク一覧）を表示
@app.route('/')
def index():
    tasks = Task.query.all()  # すべてのタスクを取得
    return render_template('index.html', tasks=tasks)

# 新しいタスクを追加する処理
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')  # タスクのタイトルを取得
    description = request.form.get('description')  # タスクの説明を取得
    
    # 新しいタスクを作成してデータベースに追加
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    
    # タスク一覧ページにリダイレクト
    return redirect(url_for('index'))

# タスクを削除する処理
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)  # 削除するタスクを取得
    db.session.delete(task)  # タスクを削除
    db.session.commit()  # 変更をデータベースに反映
    return redirect(url_for('index'))

# タスクを完了にする処理
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)  # 完了するタスクを取得
    task.status = '完了'  # ステータスを「完了」に変更
    db.session.commit()  # 変更をデータベースに反映
    return redirect(url_for('index'))

# アプリケーションの実行
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from config import Config
from flask_login import LoginManager
from database import db
import os

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

# 确保static目录存在
os.makedirs('static', exist_ok=True)

# 导入模型（必须在db初始化之后）
from models import User, Patient, FollowupRecord, SystemSetting

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功")
            # 初始化示例数据
            try:
                init_sample_data()
                print("示例数据初始化成功")
            except Exception as e:
                print(f"示例数据初始化错误: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"数据库初始化错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n启动Flask应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止应用\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)


# IgA肾病随访系统

一个基于Flask的IgA肾病患者随访管理系统，用于临床医生管理患者信息和随访记录。

## 功能特性

- **患者管理**：添加、编辑、查看和删除患者信息
- **随访记录**：记录和管理患者的随访信息，包括症状、体征、实验室检查、用药情况等
- **工作人员管理**：管理员可以管理工作人员账户（仅管理员可见）
- **系统设置**：管理员可以配置系统设置（仅管理员可见）
- **用户认证**：基于Flask-Login的用户登录系统
- **数据统计**：首页显示患者总数、随访记录总数等统计信息

## 技术栈

- **后端框架**：Flask 3.0.0
- **数据库**：SQLite + SQLAlchemy ORM
- **前端框架**：Bootstrap 5.3.8
- **图标库**：Font Awesome
- **用户认证**：Flask-Login

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

应用将在 `http://127.0.0.1:5001` 启动。

**注意**：如果端口5000被占用，应用会自动使用端口5001。

### 3. 访问系统

在浏览器中打开 `http://localhost:5001`

或者使用启动脚本：
```bash
python start_app.py
```

### 4. 默认登录信息

系统初始化时会自动创建以下用户：

- **管理员账户**
  - 用户名：`admin`
  - 密码：`admin123`

- **医生账户**
  - 用户名：`doctor1`
  - 密码：`123456`

- **护士账户**
  - 用户名：`nurse1`
  - 密码：`123456`

## 项目结构

```
IgA_fellowup_sys/
├── app.py                 # Flask应用主文件
├── config.py              # 配置文件
├── database.py            # 数据库初始化
├── models.py              # 数据库模型
├── routes.py              # 路由和视图函数
├── requirements.txt       # Python依赖
├── templates/             # HTML模板
│   ├── base.html          # 基础模板
│   ├── login.html         # 登录页
│   ├── dashboard.html     # 首页/仪表盘
│   ├── patients.html      # 患者列表
│   ├── patient_form.html  # 患者表单
│   ├── patient_detail.html # 患者详情
│   ├── records.html       # 随访记录列表
│   ├── record_form.html   # 随访记录表单
│   ├── record_detail.html # 随访记录详情
│   ├── staff.html         # 工作人员列表
│   ├── staff_form.html    # 工作人员表单
│   └── settings.html      # 系统设置
├── static/                # 静态资源
│   ├── css/               # Bootstrap CSS
│   ├── js/                # Bootstrap JS
│   └── cdnjs/             # Font Awesome
└── iga_followup.db        # SQLite数据库（运行后自动生成）
```

## 数据库模型

### User（用户/工作人员）
- 用户名、密码、真实姓名、角色、科室、联系方式等

### Patient（患者）
- 患者编号、姓名、性别、年龄、诊断信息、病史等

### FollowupRecord（随访记录）
- 随访日期、症状、体征、实验室检查结果、用药情况等

### SystemSetting（系统设置）
- 设置键、设置值、描述等

## 用户角色

- **admin**：管理员，可以访问所有功能，包括工作人员管理和系统设置
- **doctor**：医生，可以管理患者和随访记录
- **nurse**：护士，可以管理患者和随访记录
- **staff**：普通工作人员，可以管理患者和随访记录

## 注意事项

1. 首次运行时会自动创建数据库和示例数据
2. 数据库文件 `iga_followup.db` 会在项目根目录自动生成
3. 所有静态资源（CSS、JS、字体等）已下载到本地 `static/` 目录
4. 系统使用简体中文界面

## 开发说明

- 使用Flask-SQLAlchemy进行数据库操作
- 使用Flask-Login进行用户认证
- 使用Bootstrap 5进行前端UI设计
- 使用Font Awesome提供图标支持

## 许可证

本项目仅供学习和研究使用。


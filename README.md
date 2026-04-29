# 诊所信息系统

服务于个体诊所的单机信息系统，支持病人管理、处方管理、药品管理。

## 功能

- 病人信息管理（姓名、性别、年龄、住址、电话、过敏史）
- 处方管理（诊断、处方明细、医生、配药、复核、费用、打印）
- 药品管理（常用药品、价格）
- 数据备份

## 技术栈

- Python 3.9+
- Flask + SQLAlchemy
- SQLite
- Bootstrap 5

## 开发运行

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 运行开发服务器
python app.py
```

## 打包为exe

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

## 目录结构

```
clinic_is/
├── app.py              # 主应用入口
├── models.py           # 数据模型
├── init_db.py          # 数据库初始化
├── requirements.txt    # 依赖
├── templates/          # HTML模板
│   ├── base.html
│   ├── index.html
│   ├── patients/
│   ├── prescriptions/
│   └── drugs/
├── static/             # 静态资源
│   ├── css/
│   └── js/
└── clinic.db           # SQLite数据库
```

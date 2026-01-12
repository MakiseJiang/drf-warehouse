# 本地安装与运行

## 依赖安装

- 安装 Python 3.11+
- 在项目根目录执行：

```
pip install -r requirements.txt
```

## 初始化数据库

```
python manage.py makemigrations inventory
python manage.py migrate
```

## 创建默认管理员账户

```
python manage.py create_admin
```

## 填充初始测试数据

```
python manage.py seed
```

## 启动服务

```
python manage.py runserver
```

服务默认监听 `http://127.0.0.1:8000/`，API 位于 `http://127.0.0.1:8000/api/`。
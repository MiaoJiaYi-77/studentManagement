# 学生管理系统

## 项目简介
本项目是一个基于Python和Tkinter开发的学生管理系统，支持学生、教师和管理员三种角色，提供课程管理、成绩管理、考勤管理、通知公告等功能。

## 功能模块
- **学生模块**：个人信息查询、课程选择、成绩查询、考勤查询、奖惩记录查询、公告通知查看。
- **教师模块**：课程信息管理、成绩录入、课程安排、选课名单查看、公告发布。
- **管理员模块**：用户管理、学生管理、教师管理、班级管理、课程管理、选课管理、成绩管理、通知管理、数据分析。



## 数据库配置
1. 确保已安装MySQL数据库。
2. 在MySQL中创建数据库：
   ```sql
   CREATE DATABASE student_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. 使用项目中的`init.sql`文件初始化数据库：
   ```
   mysql -u root -p student_management_system < init.sql
   ```
4. 修改`db_config.py`中的数据库连接配置：
   ```python
   config = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',  # 修改为你的数据库密码
       'database': 'student_management_system'
   }
   ```

## 运行说明
1. 启动程序：
   ```
   python login_system.py
   ```
2. 使用默认账号登录：
   - 管理员：用户名 `admin`，密码 `123456`
   - 教师：用户名 `teacher1`，密码 `123456`
   - 学生：用户名 `student1`，密码 `123456`

## 项目结构
- `login_system.py`：登录系统入口
- `main_window.py`：主窗口界面
- `db_config.py`：数据库配置
- `init.sql`：数据库初始化脚本
- `admin/`：管理员模块
- `teacher/`：教师模块
- `student/`：学生模块
- `styles/`：界面样式

## 依赖库
- customtkinter：现代化UI界面
- mysql-connector-python：MySQL数据库连接
- matplotlib：数据可视化
- pandas：数据分析

## 注意事项
- 请确保MySQL服务已启动。
- 首次运行前请先初始化数据库。
- 如遇到中文显示问题，请确保系统安装了中文字体。 
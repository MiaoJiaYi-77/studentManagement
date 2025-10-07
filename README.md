# 学生管理系统

## 项目简介
本项目是一个基于Python和Tkinter开发的学生管理系统，支持学生、教师和管理员三种角色，提供课程管理、成绩管理、考勤管理、通知公告等功能。

<img width="531" height="444" alt="image" src="https://github.com/user-attachments/assets/e8ba97a9-3121-4437-8478-457c2b96ab9b" />
<img width="613" height="556" alt="image" src="https://github.com/user-attachments/assets/e387b52e-36a3-4afc-ab52-53f1a4a74573" />
<img width="865" height="456" alt="image" src="https://github.com/user-attachments/assets/df5f2de8-3f77-4513-9e0d-bb75347e5085" />
<img width="865" height="459" alt="image" src="https://github.com/user-attachments/assets/4ab8f659-d6bc-4c8c-9e76-37b0d92bc8c3" />
<img width="865" height="455" alt="image" src="https://github.com/user-attachments/assets/013167c4-ea7f-4698-b8ac-9dd161dd01cd" />
<img width="865" height="460" alt="image" src="https://github.com/user-attachments/assets/e91e3702-d112-49d1-b2ff-36307596d36b" />
<img width="865" height="457" alt="image" src="https://github.com/user-attachments/assets/e007e129-21ca-4c7b-887c-5b644d5c5979" />
<img width="865" height="460" alt="image" src="https://github.com/user-attachments/assets/df4491a3-433f-484c-8b4f-2b35e644b316" />
<img width="865" height="459" alt="image" src="https://github.com/user-attachments/assets/8f7aa1af-f527-487f-9fa9-12db542b5c78" />
<img width="865" height="458" alt="image" src="https://github.com/user-attachments/assets/fa3c16f4-2b9e-4b6d-b7cf-6b1d88a10037" />
<img width="865" height="457" alt="image" src="https://github.com/user-attachments/assets/a88a8ab3-2b45-4c21-83a4-e08062c94d38" />
<img width="865" height="457" alt="image" src="https://github.com/user-attachments/assets/0f59c4e3-96de-4cf2-b0a5-281913db52c9" />
<img width="865" height="457" alt="image" src="https://github.com/user-attachments/assets/e5f97190-2916-475f-85b1-49b135f5a644" />
<img width="865" height="458" alt="image" src="https://github.com/user-attachments/assets/478c0bd1-839f-41a9-a5b8-224f0bebb748" />

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

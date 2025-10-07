import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class StudentManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用样式
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="学生管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增学生", 
                                    command=self.add_student,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑学生", 
                                     command=self.edit_student,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除学生", 
                                       command=self.delete_student,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_students,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "name", "gender", "birth", "class_name", "phone", "email", 
                  "address", "enroll_date", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16, style="Form.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置表头
        column_text = {
            "id": "学生ID", 
            "name": "姓名",
            "gender": "性别",
            "birth": "出生日期",
            "class_name": "班级",
            "phone": "电话",
            "email": "邮箱",
            "address": "地址",
            "enroll_date": "入学日期",
            "status": "状态"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col], anchor=tk.CENTER)
            # 根据内容类型设置列宽
            if col in ["id", "gender", "status"]:
                width = 80
            elif col in ["birth", "enroll_date"]:
                width = 100
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_student())

    def refresh_students(self):
        """刷新学生列表"""
        try:
            # 禁用刷新按钮，防止重复点击
            self.refresh_btn.configure(state="disabled")
            
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.name, s.gender, s.birth, c.name as class_name, 
                       s.phone, s.email, s.address, s.enroll_date, s.status
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                ORDER BY s.id
            """)
            
            # 填充数据
            for row in cursor.fetchall():
                # 转换日期格式为字符串显示
                display_row = list(row)
                if row[3]:  # birth
                    display_row[3] = row[3].strftime('%Y-%m-%d')
                if row[8]:  # enroll_date
                    display_row[8] = row[8].strftime('%Y-%m-%d')
                self.tree.insert('', tk.END, values=display_row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.configure(state="normal")
            
    def load_students(self):
        """加载学生列表（包装方法）"""
        self.refresh_students()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_students()
        form.destroy()

    def add_student(self):
        self.open_student_form()

    def edit_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的学生！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_student_form(values)

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的学生！")
            return
        
        student_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {student_id} 的学生吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 开始事务
            conn.start_transaction()
            
            # 删除学生表数据
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            
            # 删除用户表数据
            cursor.execute("DELETE FROM users WHERE id = %s", (student_id,))
            
            # 提交事务
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_students()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_student_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑学生" if is_edit else "新增学生")
        
        # 设置模态
        form.grab_set()
        form.transient(self.parent_frame)
        
        # 居中显示 - 调整窗口大小为更宽更高
        self.center_window(form, 550, 700)
        
        # 创建表单框架
        form_frame = ctk.CTkFrame(form, fg_color="#f8f9fa")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 存储变量
        self.field_vars = {}
        
        # 如果是新增，先选择用户
        row_index = 0
        if not is_edit:
            ctk.CTkLabel(form_frame, text="选择用户：", 
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=row_index, column=0, pady=10, sticky="e")
            user_var = tk.StringVar(form)
            user_combo = ctk.CTkOptionMenu(form_frame, variable=user_var,
                                         width=200, height=32,
                                         font=ctk.CTkFont(family="微软雅黑", size=12),
                                         fg_color="#4a90e2",
                                         button_color="#357abd",
                                         button_hover_color="#2980b9")
            user_combo.grid(row=row_index, column=1, pady=10, sticky="w")
            row_index += 1
            
            # 获取可用的学生用户
            try:
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.id, u.username 
                    FROM users u 
                    LEFT JOIN students s ON u.id = s.id
                    WHERE u.role = '学生' AND s.id IS NULL
                    ORDER BY u.id
                """)
                users = cursor.fetchall()
                if not users:
                    messagebox.showerror("错误", "没有可用的学生用户！请先在用户管理中添加学生用户。")
                    form.destroy()
                    return
                
                user_options = [f"{user[0]} - {user[1]}" for user in users]
                user_combo.configure(values=user_options)
                if user_options:
                    user_combo.set(user_options[0])
                self.field_vars['user'] = user_var
                
            except Exception as e:
                messagebox.showerror("错误", f"获取用户列表失败：{str(e)}")
                form.destroy()
                return
            finally:
                if 'conn' in locals():
                    conn.close()
        
        # 创建输入字段
        fields = [
            ("姓名：", "name", values[1] if is_edit else ""),
            ("性别：", "gender", values[2] if is_edit else "男"),
            ("出生日期：", "birth", values[3] if is_edit else ""),
            ("班级：", "class", values[4] if is_edit else ""),
            ("电话：", "phone", values[5] if is_edit else ""),
            ("邮箱：", "email", values[6] if is_edit else ""),
            ("地址：", "address", values[7] if is_edit else ""),
            ("入学日期：", "enroll_date", values[8] if is_edit else ""),
            ("状态：", "status", values[9] if is_edit else "在读")
        ]
        
        # 创建输入框
        for i, (label_text, field_name, default_value) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label_text, 
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=row_index+i, column=0, pady=10, sticky="e")
            
            if field_name == "gender":
                var = tk.StringVar(form, value=default_value)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        values=["男", "女"],
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=row_index+i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
            elif field_name == "status":
                var = tk.StringVar(form, value=default_value)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        values=["在读", "毕业", "休学", "退学"],
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=row_index+i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
            elif field_name == "class":
                var = tk.StringVar(form)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=row_index+i, column=1, pady=10, sticky="w")
                
                # 获取班级列表
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name FROM classes ORDER BY id")
                    classes = cursor.fetchall()
                    if classes:
                        class_options = [f"{c[0]} - {c[1]}" for c in classes]
                        combo.configure(values=class_options)
                        if is_edit and default_value:
                            # 查找对应的班级ID
                            cursor.execute("SELECT id FROM classes WHERE name = %s", (default_value,))
                            class_id = cursor.fetchone()
                            if class_id:
                                for class_item in class_options:
                                    if class_item.startswith(f"{class_id[0]} -"):
                                        combo.set(class_item)
                                        break
                        elif class_options:
                            combo.set(class_options[0])
                except Exception as e:
                    messagebox.showerror("错误", f"获取班级列表失败：{str(e)}")
                finally:
                    if 'conn' in locals():
                        conn.close()
                
                self.field_vars[field_name] = var
            else:
                var = tk.StringVar(form, value=default_value)
                entry = ctk.CTkEntry(form_frame, textvariable=var,
                                   width=200, height=32,
                                   font=ctk.CTkFont(family="微软雅黑", size=12))
                entry.grid(row=row_index+i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row_index+len(fields), column=0, columnspan=2, pady=20)
        
        def on_submit(event=None):
            try:
                # 获取并验证输入
                data = {field: var.get().strip() for field, var in self.field_vars.items()}
                
                # 验证必填字段
                if not data['name']:
                    messagebox.showerror("错误", "姓名不能为空！")
                    return
                
                if not is_edit and not data.get('user'):
                    messagebox.showerror("错误", "请选择用户！")
                    return
                
                # 验证日期格式
                for date_field in ['birth', 'enroll_date']:
                    try:
                        if data[date_field]:
                            datetime.strptime(data[date_field], '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("错误", f"{'出生' if date_field == 'birth' else '入学'}日期格式不正确，请使用YYYY-MM-DD格式！")
                        return
                
                # 获取班级ID
                class_id = None
                if data['class']:
                    class_id = data['class'].split(' - ')[0]
                
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    
                    if is_edit:
                        # 更新学生信息
                        cursor.execute("""
                            UPDATE students 
                            SET name=%s, gender=%s, birth=%s, class_id=%s, phone=%s,
                                email=%s, address=%s, enroll_date=%s, status=%s 
                            WHERE id=%s
                        """, (
                            data['name'], data['gender'], 
                            data['birth'] or None, class_id,
                            data['phone'], data['email'], data['address'],
                            data['enroll_date'] or None, data['status'],
                            values[0]
                        ))
                        conn.commit()
                        messagebox.showinfo("成功", "保存成功！")
                        self.load_students()
                        form.destroy()
                    else:
                        # 获取选择的用户ID
                        user_id = data['user'].split(' - ')[0]
                        
                        # 创建学生信息
                        cursor.execute("""
                            INSERT INTO students (id, name, gender, birth, class_id,
                                               phone, email, address, enroll_date, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            user_id, data['name'], data['gender'],
                            data['birth'] or None, class_id,
                            data['phone'], data['email'], data['address'],
                            data['enroll_date'] or None, data['status']
                        ))
                        
                        conn.commit()
                        messagebox.showinfo("成功", "添加成功！")
                        self.load_students()
                        form.destroy()
                    
                except mysql.connector.Error as e:
                    conn.rollback()
                    messagebox.showerror("数据库错误", f"保存失败：{str(e)}\n错误代码：{e.errno}")
                    return
                except Exception as e:
                    messagebox.showerror("未知错误", f"发生未知错误：{str(e)}")
                    return
                finally:
                    if 'conn' in locals():
                        conn.close()
                        
            except Exception as e:
                messagebox.showerror("错误", f"操作失败：{str(e)}")
        
        # 绑定回车键到提交按钮
        form.bind('<Return>', on_submit)
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=on_submit,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     width=100, height=32,
                     fg_color="#4a90e2",
                     hover_color="#357abd").pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        ctk.CTkButton(btn_frame, text="取消", 
                     command=lambda: self.on_form_close(form),
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color="#f0f0f0",
                     text_color="#333333",
                     hover_color="#e0e0e0",
                     width=100, height=32).pack(side=tk.LEFT, padx=10)
        
        # 防止窗口被关闭时的验证错误
        form.protocol("WM_DELETE_WINDOW", lambda: self.on_form_close(form))

    def center_window(self, window, width, height):
        """使窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算窗口位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口大小和位置
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 设置最小尺寸
        window.minsize(width, height)
        
        # 禁止调整大小
        window.resizable(False, False) 
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles


class TeacherManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_teachers()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="教师管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增教师", 
                                    command=self.add_teacher,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑教师", 
                                     command=self.edit_teacher,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除教师", 
                                       command=self.delete_teacher,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_teachers,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "name", "gender", "phone", "email", "hire_date", "professional_title")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16, style="Form.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置表头
        column_text = {
            "id": "教师ID",
            "name": "姓名",
            "gender": "性别",
            "phone": "电话",
            "email": "邮箱",
            "hire_date": "入职日期",
            "professional_title": "职称"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id", "gender"]:
                width = 80
            elif col in ["hire_date", "professional_title"]:
                width = 120
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_teacher())

    def refresh_teachers(self):
        """刷新教师列表"""
        try:
            # 禁用刷新按钮，防止重复点击
            self.refresh_btn.configure(state='disabled')

            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, gender, phone, email, hire_date, professional_title
                FROM teachers 
                ORDER BY id
            """)

            # 填充数据
            for row in cursor.fetchall():
                # 转换日期格式为字符串显示
                display_row = list(row)
                if row[5]:  # hire_date
                    display_row[5] = row[5].strftime('%Y-%m-%d')
                self.tree.insert('', tk.END, values=display_row)

        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.configure(state='normal')

    def load_teachers(self):
        """加载教师列表（包装方法）"""
        self.refresh_teachers()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_teachers()
        form.destroy()

    def add_teacher(self):
        self.open_teacher_form()

    def edit_teacher(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的教师！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_teacher_form(values)

    def delete_teacher(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的教师！")
            return

        teacher_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {teacher_id} 的教师吗？"):
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 检查是否是某个班级的班主任
            cursor.execute("SELECT COUNT(*) FROM classes WHERE head_teacher_id = %s", (teacher_id,))
            class_count = cursor.fetchone()[0]
            if class_count > 0:
                messagebox.showerror("错误", f"该教师是 {class_count} 个班级的班主任，无法删除！")
                return

            # 开始事务
            conn.start_transaction()

            # 删除教师表数据
            cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))

            # 删除用户表数据
            cursor.execute("DELETE FROM users WHERE id = %s", (teacher_id,))

            # 提交事务
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_teachers()

        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_teacher_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑教师" if is_edit else "新增教师")
        
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
            
            # 获取可用的教师用户
            try:
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.id, u.username 
                    FROM users u 
                    LEFT JOIN teachers t ON u.id = t.id
                    WHERE u.role = '教师' AND t.id IS NULL
                    ORDER BY u.id
                """)
                users = cursor.fetchall()
                if not users:
                    messagebox.showerror("错误", "没有可用的教师用户！请先在用户管理中添加教师用户。")
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
            ("电话：", "phone", values[3] if is_edit else ""),
            ("邮箱：", "email", values[4] if is_edit else ""),
            ("入职日期：", "hire_date", values[5] if is_edit else ""),
            ("职称：", "professional_title", values[6] if is_edit else "")
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
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=lambda: self.save_teacher(form, values[0] if is_edit else None),
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
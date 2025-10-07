import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class UserManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用样式
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="用户管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增用户", 
                                    command=self.add_user,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑用户", 
                                     command=self.edit_user,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除用户", 
                                       command=self.delete_user,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_users,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        import tkinter.ttk as ttk
        columns = ("id", "username", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16, style="Form.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置表头
        column_text = {"id": "用户ID", "username": "用户名", "role": "角色"}
        for col in columns:
            self.tree.heading(col, text=column_text[col], anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER, width=120, minwidth=100)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_user())

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

    def open_user_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑用户" if is_edit else "新增用户")
        
        # 设置模态
        form.grab_set()
        form.transient(self.parent_frame)
        
        # 居中显示
        self.center_window(form, 400, 300)
        
        # 创建表单框架
        form_frame = ctk.CTkFrame(form, fg_color="#f8f9fa")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 用户名
        ctk.CTkLabel(form_frame, text="用户名：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=0, pady=10, sticky="e")
        username_var = tk.StringVar(value=values[1] if values else "")
        username_entry = ctk.CTkEntry(form_frame, textvariable=username_var, 
                                    width=200, height=32,
                                    font=ctk.CTkFont(family="微软雅黑", size=12))
        username_entry.grid(row=0, column=1, pady=10, sticky="w")
        
        # 角色
        ctk.CTkLabel(form_frame, text="角色：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=1, column=0, pady=10, sticky="e")
        role_var = tk.StringVar(value=values[2] if values else "学生")
        role_combo = ctk.CTkOptionMenu(form_frame, variable=role_var,
                                     values=["管理员", "教师", "学生"],
                                     width=200, height=32,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     fg_color="#4a90e2",
                                     button_color="#357abd",
                                     button_hover_color="#2980b9")
        role_combo.grid(row=1, column=1, pady=10, sticky="w")
        
        # 密码（新增时显示）
        if not is_edit:
            ctk.CTkLabel(form_frame, text="密码：", 
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=2, column=0, pady=10, sticky="e")
            pwd_var = tk.StringVar()
            pwd_entry = ctk.CTkEntry(form_frame, textvariable=pwd_var, show="*",
                                   width=200, height=32,
                                   font=ctk.CTkFont(family="微软雅黑", size=12))
            pwd_entry.grid(row=2, column=1, pady=10, sticky="w")
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def on_submit(event=None):
            try:
                username = username_entry.get().strip()
                role = role_combo.get()
                
                # 验证输入
                if username == "":
                    messagebox.showerror("错误", "用户名不能为空！")
                    username_entry.focus()
                    return
                    
                if not role:
                    messagebox.showerror("错误", "请选择用户角色！")
                    role_combo.focus()
                    return
                    
                if not is_edit and not pwd_entry.get().strip():
                    messagebox.showerror("错误", "密码不能为空！")
                    pwd_entry.focus()
                    return
                    
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    
                    if is_edit:
                        cursor.execute("UPDATE users SET username=%s, role=%s WHERE id=%s",
                                     (username, role, values[0]))
                        conn.commit()
                        messagebox.showinfo("成功", "保存成功！")
                        self.load_users()
                        form.destroy()
                    else:
                        # 检查用户名是否已存在
                        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
                        if cursor.fetchone():
                            messagebox.showerror("错误", "该用户名已存在！")
                            username_entry.focus()
                            return
                            
                        # 插入新用户
                        import hashlib
                        hashed_pwd = hashlib.sha256(pwd_entry.get().encode()).hexdigest()
                        cursor.execute("""
                            INSERT INTO users (username, password, role)
                            VALUES (%s, %s, %s)
                        """, (username, hashed_pwd, role))
                        conn.commit()
                        messagebox.showinfo("成功", "保存成功！")
                        self.load_users()
                        form.destroy()
                        
                except mysql.connector.Error as e:
                    if e.errno == 1062:
                        messagebox.showerror("错误", "该用户名已存在！")
                    else:
                        messagebox.showerror("数据库错误", f"保存失败：{str(e)}")
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
        
        # 设置初始焦点
        username_entry.focus()
            
        # 防止窗口被关闭时的验证错误
        form.protocol("WM_DELETE_WINDOW", lambda: self.on_form_close(form))

    def refresh_users(self):
        """刷新用户列表"""
        try:
            # 禁用刷新按钮，防止重复点击
            self.refresh_btn.configure(state="disabled")
            
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users ORDER BY id")
            
            # 填充数据
            for row in cursor.fetchall():
                self.tree.insert('', tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.configure(state="normal")
            
    def load_users(self):
        """加载用户列表（包装方法）"""
        self.refresh_users()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_users()
        form.destroy()

    def add_user(self):
        self.open_user_form()

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的用户！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_user_form(values)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的用户！")
            return
        
        user_id = self.tree.item(selected[0], 'values')[0]
        user_role = self.tree.item(selected[0], 'values')[2]
        
        # 检查是否删除管理员
        if user_role == "管理员":
            try:
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE role='管理员'")
                admin_count = cursor.fetchone()[0]
                if admin_count <= 1:
                    messagebox.showerror("错误", "系统至少需要保留一个管理员账号！")
                    return
            except Exception as e:
                messagebox.showerror("错误", f"检查管理员失败：{str(e)}")
                return
            finally:
                if 'conn' in locals():
                    conn.close()
        
        if not messagebox.askyesno("确认", f"确定要删除ID为 {user_id} 的用户吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 开始事务
            conn.start_transaction()
            
            # 根据角色删除相关表数据
            if user_role == "学生":
                cursor.execute("DELETE FROM students WHERE id=%s", (user_id,))
            elif user_role == "教师":
                cursor.execute("DELETE FROM teachers WHERE id=%s", (user_id,))
            
            # 删除用户表数据
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            
            # 提交事务
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_users()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
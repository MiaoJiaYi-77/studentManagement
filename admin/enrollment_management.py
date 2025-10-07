import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class EnrollmentManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_enrollments()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="选课管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增选课", 
                                    command=self.add_enrollment,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑选课", 
                                     command=self.edit_enrollment,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除选课", 
                                       command=self.delete_enrollment,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_enrollments,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "student_name", "course_name", "enroll_time", "status", "score")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16,
                                style="Form.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置表头
        column_text = {
            "id": "选课ID", 
            "student_name": "学生姓名",
            "course_name": "课程名称",
            "enroll_time": "选课时间",
            "status": "状态",
            "score": "成绩"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id", "status"]:
                width = 80
            elif col in ["score"]:
                width = 100
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_enrollment())

    def refresh_enrollments(self):
        """刷新选课列表"""
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
                SELECT e.id, CONCAT(s.name, ' (ID:', s.id, ')') as student_name,
                       CONCAT(c.name, ' (ID:', c.id, ')') as course_name,
                       e.enroll_time, e.status,
                       COALESCE(sc.score, '未录入') as score
                FROM enrollments e
                JOIN students s ON e.student_id = s.id
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN scores sc ON e.id = sc.enrollment_id
                ORDER BY e.id
            """)
            
            # 填充数据
            for row in cursor.fetchall():
                # 转换日期格式为字符串显示
                display_row = list(row)
                if row[3]:  # enroll_time
                    display_row[3] = row[3].strftime('%Y-%m-%d')
                self.tree.insert('', tk.END, values=display_row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.configure(state='normal')
            
    def load_enrollments(self):
        """加载选课列表（包装方法）"""
        self.refresh_enrollments()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_enrollments()
        form.destroy()

    def add_enrollment(self):
        self.open_enrollment_form()

    def edit_enrollment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的选课记录！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_enrollment_form(values)

    def delete_enrollment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的选课记录！")
            return
        
        enrollment_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {enrollment_id} 的选课记录吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 开始事务
            conn.start_transaction()
            
            # 删除成绩记录
            cursor.execute("DELETE FROM scores WHERE enrollment_id = %s", (enrollment_id,))
            
            # 删除选课记录
            cursor.execute("DELETE FROM enrollments WHERE id = %s", (enrollment_id,))
            
            # 提交事务
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_enrollments()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_enrollment_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑选课" if is_edit else "新增选课")
        
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
        
        # 创建输入字段
        fields = [
            ("学生：", "student", values[1] if is_edit else ""),
            ("课程：", "course", values[2] if is_edit else ""),
            ("选课时间：", "enroll_time", values[3] if is_edit else datetime.now().strftime('%Y-%m-%d')),
            ("状态：", "status", values[4] if is_edit else "已选")
        ]
        
        # 创建输入框
        for i, (label_text, field_name, default_value) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label_text, 
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i, column=0, pady=10, sticky="e")
            
            if field_name == "student" and not is_edit:
                var = tk.StringVar(form)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=i, column=1, pady=10, sticky="w")
                
                # 获取学生列表
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name FROM students ORDER BY id")
                    students = cursor.fetchall()
                    if students:
                        student_options = [f"{s[0]} - {s[1]}" for s in students]
                        combo.configure(values=student_options)
                except Exception as e:
                    messagebox.showerror("错误", f"获取学生列表失败：{str(e)}")
                finally:
                    if 'conn' in locals():
                        conn.close()
                
                self.field_vars[field_name] = var
            elif field_name == "course" and not is_edit:
                var = tk.StringVar(form)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=i, column=1, pady=10, sticky="w")
                
                # 获取课程列表
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name FROM courses ORDER BY id")
                    courses = cursor.fetchall()
                    if courses:
                        course_options = [f"{c[0]} - {c[1]}" for c in courses]
                        combo.configure(values=course_options)
                except Exception as e:
                    messagebox.showerror("错误", f"获取课程列表失败：{str(e)}")
                finally:
                    if 'conn' in locals():
                        conn.close()
                
                self.field_vars[field_name] = var
            elif field_name == "status":
                var = tk.StringVar(form, value=default_value)
                combo = ctk.CTkOptionMenu(form_frame, variable=var,
                                        values=["已选", "退选"],
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
                combo.grid(row=i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
            else:
                if is_edit:
                    # 编辑模式下显示只读文本
                    ctk.CTkLabel(form_frame, text=default_value, 
                               font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i, column=1, pady=10, sticky="w")
                    self.field_vars[field_name] = tk.StringVar(value=default_value)
                else:
                    var = tk.StringVar(form, value=default_value)
                    entry = ctk.CTkEntry(form_frame, textvariable=var,
                                       width=200, height=32,
                                       font=ctk.CTkFont(family="微软雅黑", size=12))
                    entry.grid(row=i, column=1, pady=10, sticky="w")
                    self.field_vars[field_name] = var
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=lambda: self.save_enrollment(form, values[0] if is_edit else None),
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
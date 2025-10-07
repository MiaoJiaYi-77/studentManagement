import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from .course_schedule_management import CourseScheduleManagement
import customtkinter as ctk

class CourseManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="课程管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增课程", 
                                    command=self.add_course,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑课程", 
                                     command=self.edit_course,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除课程", 
                                       command=self.delete_course,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.time_btn = ctk.CTkButton(btn_frame, text="时间管理", 
                                     command=self.manage_course_schedule,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.time_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_courses,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "name", "teacher_name", "credit", "capacity")
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
            "id": "课程ID", 
            "name": "课程名称",
            "teacher_name": "授课教师",
            "credit": "学分",
            "capacity": "容量"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id", "credit", "capacity"]:
                width = 80
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_course())

    def refresh_courses(self):
        """刷新课程列表"""
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
                SELECT c.id, c.name, CONCAT(t.name, ' (ID:', t.id, ')') as teacher_name,
                       c.credit, c.capacity
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                ORDER BY c.id
            """)
            
            # 填充数据
            for row in cursor.fetchall():
                self.tree.insert('', tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.configure(state='normal')
            
    def load_courses(self):
        """加载课程列表（包装方法）"""
        self.refresh_courses()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_courses()
        form.destroy()

    def add_course(self):
        self.open_course_form()

    def edit_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的课程！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_course_form(values)

    def delete_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的课程！")
            return
        
        course_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {course_id} 的课程吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 检查是否有学生选择了这门课程
            cursor.execute("SELECT COUNT(*) FROM enrollments WHERE course_id = %s", (course_id,))
            enrollment_count = cursor.fetchone()[0]
            if enrollment_count > 0:
                messagebox.showerror("错误", f"该课程已有 {enrollment_count} 名学生选课，无法删除！")
                return
            
            # 检查是否有课程时间安排
            cursor.execute("SELECT COUNT(*) FROM course_schedule WHERE course_id = %s", (course_id,))
            schedule_count = cursor.fetchone()[0]
            if schedule_count > 0:
                messagebox.showerror("错误", f"该课程已有 {schedule_count} 条时间安排，请先删除相关时间安排！")
                return
            
            # 删除课程
            cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_courses()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def manage_course_schedule(self):
        """管理课程时间安排"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要管理时间的课程！")
            return
            
        # 获取选中的课程信息
        course_id = self.tree.item(selected[0], 'values')[0]
        course_name = self.tree.item(selected[0], 'values')[1]
        
        # 清空当前内容
        self.clear_content()
        
        # 创建课程时间管理界面
        CourseScheduleManagement(self.frame, course_id, course_name)
        
    def clear_content(self):
        """清空当前内容"""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def open_course_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑课程" if is_edit else "新增课程")
        
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
            ("课程名称：", "name", values[1] if is_edit else ""),
            ("学分：", "credit", values[3] if is_edit else ""),
            ("容量：", "capacity", values[4] if is_edit else "")
        ]
        
        # 创建输入框
        for i, (label_text, field_name, default_value) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label_text, 
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i, column=0, pady=10, sticky="e")
            var = tk.StringVar(form, value=default_value)
            entry = ctk.CTkEntry(form_frame, textvariable=var,
                               width=200, height=32,
                               font=ctk.CTkFont(family="微软雅黑", size=12))
            entry.grid(row=i, column=1, pady=10, sticky="w")
            self.field_vars[field_name] = var
        
        # 教师选择
        ctk.CTkLabel(form_frame, text="授课教师：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=len(fields), column=0, pady=10, sticky="e")
        teacher_var = tk.StringVar(form)
        teacher_combo = ctk.CTkOptionMenu(form_frame, variable=teacher_var,
                                        width=200, height=32,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9")
        teacher_combo.grid(row=len(fields), column=1, pady=10, sticky="w")
        self.field_vars['teacher'] = teacher_var
        
        # 获取教师列表
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM teachers ORDER BY id")
            teachers = cursor.fetchall()
            if teachers:
                teacher_options = [f"{t[0]} - {t[1]}" for t in teachers]
                teacher_combo.configure(values=teacher_options)
                if is_edit and values[2]:  # 如果是编辑模式且有教师
                    # 从 "张三 (ID:1)" 格式中提取ID和名称
                    import re
                    match = re.search(r'(.*) \(ID:(\d+)\)', values[2])
                    if match:
                        teacher_name, teacher_id = match.group(1), match.group(2)
                        for option in teacher_options:
                            if option.startswith(f"{teacher_id} -"):
                                teacher_var.set(option)
                                break
            
        except Exception as e:
            messagebox.showerror("错误", f"获取教师列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=lambda: self.save_course(form, values[0] if is_edit else None),
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

    def save_course(self, form, course_id):
        try:
            # 获取并验证输入
            data = {field: var.get().strip() for field, var in self.field_vars.items()}
            
            # 验证必填字段
            if not data['name']:
                messagebox.showerror("错误", "课程名称不能为空！")
                return
            
            # 验证数字字段
            try:
                if data['credit']:
                    credit = float(data['credit'])
                    if credit <= 0:
                        messagebox.showerror("错误", "学分必须大于0！")
                        return
                if data['capacity']:
                    capacity = int(data['capacity'])
                    if capacity <= 0:
                        messagebox.showerror("错误", "容量必须大于0！")
                        return
            except ValueError:
                messagebox.showerror("错误", "学分和容量必须是数字！")
                return
            
            # 获取教师ID
            teacher_id = None
            if data['teacher']:
                teacher_id = data['teacher'].split(' - ')[0]
            
            try:
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                
                if course_id:
                    # 检查课程名称是否已存在（排除自身）
                    cursor.execute("SELECT id FROM courses WHERE name=%s AND id!=%s", 
                                 (data['name'], course_id))
                    if cursor.fetchone():
                        messagebox.showerror("错误", "该课程名称已存在！")
                        return
                    
                    # 更新课程信息
                    cursor.execute("""
                        UPDATE courses 
                        SET name=%s, teacher_id=%s, credit=%s, capacity=%s 
                        WHERE id=%s
                    """, (
                        data['name'], teacher_id,
                        data['credit'] or None, data['capacity'] or None,
                        course_id
                    ))
                    conn.commit()
                    messagebox.showinfo("成功", "保存成功！")
                    self.load_courses()
                    form.destroy()
                else:
                    # 检查课程名称是否已存在
                    cursor.execute("SELECT id FROM courses WHERE name=%s", (data['name'],))
                    if cursor.fetchone():
                        messagebox.showerror("错误", "该课程名称已存在！")
                        return
                    
                    # 创建课程
                    cursor.execute("""
                        INSERT INTO courses (name, teacher_id, credit, capacity)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        data['name'], teacher_id,
                        data['credit'] or None, data['capacity'] or None
                    ))
                    
                    conn.commit()
                    messagebox.showinfo("成功", "添加成功！")
                    self.load_courses()
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
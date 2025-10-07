import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class ClassManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_classes()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="班级管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="新增班级", 
                                    command=self.add_class,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑班级", 
                                     command=self.edit_class,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除班级", 
                                       command=self.delete_class,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_classes,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "name", "major", "grade", "college", "head_teacher")
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
            "id": "班级ID", 
            "name": "班级名称",
            "major": "专业",
            "grade": "年级",
            "college": "学院",
            "head_teacher": "班主任"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id"]:
                width = 80
            elif col in ["name", "major", "grade"]:
                width = 120
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_class())

    def refresh_classes(self):
        """刷新班级列表"""
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
                SELECT c.id, c.name, c.major, c.grade, c.college, 
                       CONCAT(t.name, ' (ID:', t.id, ')') as head_teacher
                FROM classes c
                LEFT JOIN teachers t ON c.head_teacher_id = t.id
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
            
    def load_classes(self):
        """加载班级列表（包装方法）"""
        self.refresh_classes()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_classes()
        form.destroy()

    def add_class(self):
        self.open_class_form()

    def edit_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的班级！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_class_form(values)

    def delete_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的班级！")
            return
        
        class_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {class_id} 的班级吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 检查是否有学生在这个班级
            cursor.execute("SELECT COUNT(*) FROM students WHERE class_id = %s", (class_id,))
            student_count = cursor.fetchone()[0]
            if student_count > 0:
                messagebox.showerror("错误", f"该班级还有 {student_count} 名学生，无法删除！")
                return
            
            # 删除班级
            cursor.execute("DELETE FROM classes WHERE id = %s", (class_id,))
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_classes()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_class_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑班级" if is_edit else "新增班级")
        
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
            ("班级名称：", "name", values[1] if is_edit else ""),
            ("专业：", "major", values[2] if is_edit else ""),
            ("年级：", "grade", values[3] if is_edit else ""),
            ("学院：", "college", values[4] if is_edit else ""),
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
        
        # 班主任选择
        ctk.CTkLabel(form_frame, text="班主任：", 
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
                if is_edit and values[5]:  # 如果是编辑模式且有班主任
                    # 从 "张三 (ID:1)" 格式中提取ID和名称
                    import re
                    match = re.search(r'(.*) \(ID:(\d+)\)', values[5])
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
                     command=lambda: self.save_class(form, values[0] if is_edit else None),
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
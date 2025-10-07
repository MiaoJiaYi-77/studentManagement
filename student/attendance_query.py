import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class AttendanceQuery:
    def __init__(self, parent_frame, student_id):
        self.parent_frame = parent_frame
        self.student_id = student_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_attendance()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="考勤信息", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建过滤框架
        filter_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # 课程筛选
        ctk.CTkLabel(filter_frame, text="课程：",
                    font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT, padx=(0, 5))
        self.course_var = tk.StringVar(value="全部")
        self.course_combobox = ctk.CTkOptionMenu(filter_frame, 
                                                variable=self.course_var,
                                                values=["全部"],
                                                width=200,
                                                font=ctk.CTkFont(family="微软雅黑", size=12),
                                                fg_color="#4a90e2",
                                                button_color="#357abd",
                                                button_hover_color="#2980b9")
        self.course_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 考勤状态筛选
        ctk.CTkLabel(filter_frame, text="状态：",
                    font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="全部")
        self.status_combobox = ctk.CTkOptionMenu(filter_frame,
                                                variable=self.status_var,
                                                values=["全部", "出勤", "迟到", "缺勤", "请假"],
                                                width=120,
                                                font=ctk.CTkFont(family="微软雅黑", size=12),
                                                fg_color="#4a90e2",
                                                button_color="#357abd",
                                                button_hover_color="#2980b9")
        self.status_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 查询按钮
        ctk.CTkButton(filter_frame, text="查询",
                     command=self.load_attendance,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     width=100,
                     height=32,
                     fg_color="#4a90e2",
                     hover_color="#357abd").pack(side=tk.LEFT)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建考勤列表
        columns = ("日期", "课程名称", "教师", "状态")
        self.attendance_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                          style="Form.Treeview")
        self.attendance_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 设置列宽和标题
        self.attendance_tree.column("日期", width=150)
        self.attendance_tree.column("课程名称", width=250)
        self.attendance_tree.column("教师", width=150)
        self.attendance_tree.column("状态", width=100)
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)

        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.attendance_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)

        # 创建统计信息框架
        stats_frame = ctk.CTkFrame(self.frame)
        stats_frame.pack(fill=tk.X, pady=10)

        # 统计信息标签
        self.stats_labels = {}
        stats_items = [
            ("total", "总课时："),
            ("present", "出勤："),
            ("late", "迟到："),
            ("absent", "缺勤："),
            ("leave", "请假："),
            ("attendance_rate", "出勤率：")
        ]

        # 创建统计信息网格
        for i, (key, text) in enumerate(stats_items):
            # 标签
            ctk.CTkLabel(stats_frame, text=text,
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i//3, column=(i%3)*2, padx=15, pady=10, sticky="e")
            # 值
            value_label = ctk.CTkLabel(stats_frame, text="--",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
            value_label.grid(row=i//3, column=(i%3)*2+1, padx=15, pady=10, sticky="w")
            self.stats_labels[key] = value_label

    def load_course_list(self):
        """加载课程列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT c.name
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                WHERE e.student_id = %s AND e.status = '已选'
                ORDER BY c.name
            """, (self.student_id,))
            
            courses = ["全部"] + [row[0] for row in cursor.fetchall()]
            self.course_combobox['values'] = courses

        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def load_attendance(self):
        """加载考勤信息"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.attendance_tree.get_children():
                self.attendance_tree.delete(item)

            # 构建查询条件
            conditions = ["a.student_id = %s"]
            params = [self.student_id]

            if self.course_var.get() != "全部":
                conditions.append("c.name = %s")
                params.append(self.course_var.get())

            if self.status_var.get() != "全部":
                conditions.append("a.status = %s")
                params.append(self.status_var.get())

            # 查询考勤信息
            query = f"""
                SELECT 
                    a.date,
                    c.name as course_name,
                    t.name as teacher_name,
                    a.status
                FROM attendance a
                JOIN courses c ON a.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                WHERE {' AND '.join(conditions)}
                ORDER BY a.date DESC
            """
            
            cursor.execute(query, tuple(params))
            attendances = cursor.fetchall()

            # 显示考勤信息
            for attendance in attendances:
                date, course_name, teacher_name, status = attendance
                self.attendance_tree.insert("", "end", values=(
                    date.strftime('%Y-%m-%d'),
                    course_name,
                    teacher_name or "未分配",
                    status
                ))

            # 计算统计信息
            stats = {
                'total': len(attendances),
                'present': sum(1 for a in attendances if a[3] == '出勤'),
                'late': sum(1 for a in attendances if a[3] == '迟到'),
                'absent': sum(1 for a in attendances if a[3] == '缺勤'),
                'leave': sum(1 for a in attendances if a[3] == '请假')
            }

            # 更新统计信息
            if stats['total'] > 0:
                attendance_rate = ((stats['present'] + stats['late']) / stats['total']) * 100
                
                self.stats_labels["total"].configure(text=str(stats['total']))
                self.stats_labels["present"].configure(text=str(stats['present']))
                self.stats_labels["late"].configure(text=str(stats['late']))
                self.stats_labels["absent"].configure(text=str(stats['absent']))
                self.stats_labels["leave"].configure(text=str(stats['leave']))
                self.stats_labels["attendance_rate"].configure(text=f"{attendance_rate:.1f}%")
            else:
                for label in self.stats_labels.values():
                    label.configure(text="--")

            # 更新课程列表
            self.load_course_list()

        except Exception as e:
            messagebox.showerror("错误", f"加载考勤信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
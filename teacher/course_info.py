import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class CourseInfo:
    def __init__(self, parent_frame, teacher_id):
        self.parent_frame = parent_frame
        self.teacher_id = teacher_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        # 创建主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="课程信息", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主内容区域
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建左侧课程列表框架
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 20), pady=10)

        # 创建课程列表
        columns = ("课程名称", "学分", "容量")
        self.course_list = ttk.Treeview(list_frame, columns=columns, show="headings", height=15,
                                      style="Form.Treeview")
        
        # 设置列宽和标题
        self.course_list.column("课程名称", width=200)
        self.course_list.column("学分", width=100)
        self.course_list.column("容量", width=100)
        
        for col in columns:
            self.course_list.heading(col, text=col)

        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.course_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.course_list.configure(yscrollcommand=scrollbar.set)
        self.course_list.pack(side=tk.LEFT, fill=tk.Y)

        # 绑定选择事件
        self.course_list.bind('<<TreeviewSelect>>', self.on_select_course)

        # 创建右侧信息框架
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # 课程详细信息
        details_frame = ctk.CTkFrame(info_frame)
        details_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        # 详情标题
        ctk.CTkLabel(details_frame, text="课程详情", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 创建详细信息标签
        self.info_labels = {}
        info_items = [
            ("name", "课程名称："),
            ("credit", "学分："),
            ("capacity", "容量："),
            ("selected", "已选人数："),
            ("remaining", "剩余名额：")
        ]

        # 创建信息网格
        info_grid = ctk.CTkFrame(details_frame, fg_color="transparent")
        info_grid.pack(pady=5)
        
        for i, (key, text) in enumerate(info_items):
            # 标签
            ctk.CTkLabel(info_grid, text=text,
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i, column=0, padx=15, pady=8, sticky="e")
            # 值
            value_label = ctk.CTkLabel(info_grid, text="--",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
            value_label.grid(row=i, column=1, padx=15, pady=8, sticky="w")
            self.info_labels[key] = value_label

        # 课程时间安排
        schedule_frame = ctk.CTkFrame(info_frame)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 时间安排标题
        ctk.CTkLabel(schedule_frame, text="上课时间", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 创建时间安排列表
        columns = ("周次", "星期", "节次", "教室")
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show="headings", height=10,
                                        style="Form.Treeview")
        
        # 设置列宽和标题
        for col in columns:
            self.schedule_tree.column(col, width=100)
            self.schedule_tree.heading(col, text=col)

        # 添加滚动条
        schedule_scrollbar = ctk.CTkScrollbar(schedule_frame, command=self.schedule_tree.yview)
        schedule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # 配置滚动条
        self.schedule_tree.configure(yscrollcommand=schedule_scrollbar.set)
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_courses(self):
        """加载教师的课程列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.course_list.get_children():
                self.course_list.delete(item)

            # 查询课程信息
            cursor.execute("""
                SELECT id, name, credit, capacity
                FROM courses
                WHERE teacher_id = %s
                ORDER BY name
            """, (self.teacher_id,))
            
            courses = cursor.fetchall()

            # 显示课程列表
            for course in courses:
                course_id, name, credit, capacity = course
                self.course_list.insert("", "end", iid=course_id, values=(
                    name,
                    credit,
                    capacity
                ))

        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def on_select_course(self, event):
        """当选择课程时显示详细信息"""
        selected_items = self.course_list.selection()
        if not selected_items:
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 查询课程详细信息
            cursor.execute("""
                SELECT 
                    c.name,
                    c.credit,
                    c.capacity,
                    COUNT(CASE WHEN e.status = '已选' THEN 1 END) as selected_count
                FROM courses c
                LEFT JOIN enrollments e ON c.id = e.course_id
                WHERE c.id = %s
                GROUP BY c.id
            """, (selected_items[0],))
            
            course = cursor.fetchone()
            if course:
                name, credit, capacity, selected_count = course
                selected_count = selected_count or 0
                remaining = capacity - selected_count

                # 更新课程信息
                self.info_labels["name"].configure(text=name)
                self.info_labels["credit"].configure(text=str(credit))
                self.info_labels["capacity"].configure(text=str(capacity))
                self.info_labels["selected"].configure(text=str(selected_count))
                self.info_labels["remaining"].configure(text=str(remaining))

                # 清空时间安排列表
                for item in self.schedule_tree.get_children():
                    self.schedule_tree.delete(item)

                # 查询课程时间安排
                cursor.execute("""
                    SELECT 
                        CONCAT(start_week, '-', end_week) as weeks,
                        weekday,
                        class_period,
                        classroom
                    FROM course_schedule
                    WHERE course_id = %s
                    ORDER BY start_week, FIELD(weekday, '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'),
                            class_period
                """, (selected_items[0],))
                
                schedules = cursor.fetchall()
                for schedule in schedules:
                    weeks, weekday, period, classroom = schedule
                    self.schedule_tree.insert("", "end", values=(
                        f"第{weeks}周",
                        weekday,
                        f"第{period}节",
                        classroom or "未安排"
                    ))

        except Exception as e:
            messagebox.showerror("错误", f"加载课程详细信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
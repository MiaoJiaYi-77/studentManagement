import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class CourseSelection:
    def __init__(self, parent_frame, student_id):
        self.parent_frame = parent_frame
        self.student_id = student_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="课程选择", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主框架
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建左右分栏
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 可选课程标题
        ctk.CTkLabel(left_frame, text="可选课程", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(0, 5))

        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 已选课程标题
        ctk.CTkLabel(right_frame, text="已选课程", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(0, 5))

        # 创建可选课程列表
        columns = ("课程ID", "课程名称", "教师", "学分", "剩余容量", "上课时间")
        self.available_courses_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15,
                                                 style="Form.Treeview")
        for col in columns:
            self.available_courses_tree.heading(col, text=col)
            if col in ["课程ID", "学分", "剩余容量"]:
                width = 80
            elif col in ["课程名称", "教师"]:
                width = 120
            else:
                width = 200
            self.available_courses_tree.column(col, width=width, minwidth=width)
        
        # 添加滚动条
        available_scrollbar = ctk.CTkScrollbar(left_frame, command=self.available_courses_tree.yview)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.available_courses_tree.configure(yscrollcommand=available_scrollbar.set)
        self.available_courses_tree.pack(fill=tk.BOTH, expand=True)

        # 创建已选课程列表
        self.selected_courses_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15,
                                                style="Form.Treeview")
        for col in columns:
            self.selected_courses_tree.heading(col, text=col)
            if col in ["课程ID", "学分", "剩余容量"]:
                width = 80
            elif col in ["课程名称", "教师"]:
                width = 120
            else:
                width = 200
            self.selected_courses_tree.column(col, width=width, minwidth=width)
        
        # 添加滚动条
        selected_scrollbar = ctk.CTkScrollbar(right_frame, command=self.selected_courses_tree.yview)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.selected_courses_tree.configure(yscrollcommand=selected_scrollbar.set)
        self.selected_courses_tree.pack(fill=tk.BOTH, expand=True)

        # 创建按钮框架
        button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # 选课按钮
        self.select_btn = ctk.CTkButton(button_frame, text="选择课程",
                                      command=self.select_course,
                                      font=ctk.CTkFont(family="微软雅黑", size=12),
                                      width=120,
                                      height=32,
                                      fg_color="#4a90e2",
                                      hover_color="#357abd")
        self.select_btn.pack(side=tk.LEFT, padx=10)

        # 退课按钮
        self.drop_btn = ctk.CTkButton(button_frame, text="退选课程",
                                    command=self.drop_course,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    width=120,
                                    height=32,
                                    fg_color="#e74c3c",
                                    hover_color="#c0392b")
        self.drop_btn.pack(side=tk.LEFT, padx=10)

    def load_courses(self):
        """加载课程信息"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.available_courses_tree.get_children():
                self.available_courses_tree.delete(item)
            for item in self.selected_courses_tree.get_children():
                self.selected_courses_tree.delete(item)

            # 查询已选课程
            cursor.execute("""
                SELECT c.id, c.name, t.name, c.credit, c.capacity, 
                       GROUP_CONCAT(
                           CONCAT(cs.weekday, ' ', cs.class_period, '节')
                           ORDER BY FIELD(cs.weekday, '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'),
                           cs.class_period
                           SEPARATOR ', '
                       ) as schedule
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN course_schedule cs ON c.id = cs.course_id
                INNER JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s AND e.status = '已选'
                GROUP BY c.id
            """, (self.student_id,))
            
            selected_courses = cursor.fetchall()
            for course in selected_courses:
                self.selected_courses_tree.insert("", "end", values=course)

            # 查询可选课程（排除已选的）
            cursor.execute("""
                SELECT 
                    c.id, 
                    c.name, 
                    t.name, 
                    c.credit, 
                    c.capacity - COALESCE(
                        (SELECT COUNT(*) 
                         FROM enrollments e2 
                         WHERE e2.course_id = c.id AND e2.status = '已选'
                        ), 0
                    ) as remaining_capacity,
                    GROUP_CONCAT(
                        CONCAT(cs.weekday, ' ', cs.class_period, '节')
                        ORDER BY FIELD(cs.weekday, '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'),
                        cs.class_period
                        SEPARATOR ', '
                    ) as schedule
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN course_schedule cs ON c.id = cs.course_id
                WHERE c.id NOT IN (
                    SELECT course_id 
                    FROM enrollments 
                    WHERE student_id = %s AND status = '已选'
                )
                GROUP BY c.id
                HAVING remaining_capacity > 0
            """, (self.student_id,))
            
            available_courses = cursor.fetchall()
            for course in available_courses:
                self.available_courses_tree.insert("", "end", values=course)

        except Exception as e:
            messagebox.showerror("错误", f"加载课程信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def select_course(self):
        """选择课程"""
        selected_item = self.available_courses_tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择要选修的课程！")
            return

        course_id = self.available_courses_tree.item(selected_item[0])['values'][0]
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 检查课程容量
            cursor.execute("""
                SELECT 
                    c.capacity - COUNT(e.id) as remaining
                FROM courses c
                LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = '已选'
                WHERE c.id = %s
                GROUP BY c.id
            """, (course_id,))
            
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                messagebox.showwarning("提示", "该课程已无剩余名额！")
                return

            # 添加选课记录
            cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, enroll_time, status)
                VALUES (%s, %s, %s, '已选')
            """, (self.student_id, course_id, datetime.now().date()))

            conn.commit()
            messagebox.showinfo("成功", "选课成功！")
            self.load_courses()  # 刷新课程列表

        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"选课失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def drop_course(self):
        """退选课程"""
        selected_item = self.selected_courses_tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择要退选的课程！")
            return

        if not messagebox.askyesno("确认", "确定要退选该课程吗？"):
            return

        course_id = self.selected_courses_tree.item(selected_item[0])['values'][0]
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 更新选课状态
            cursor.execute("""
                UPDATE enrollments 
                SET status = '退选' 
                WHERE student_id = %s AND course_id = %s AND status = '已选'
            """, (self.student_id, course_id))

            conn.commit()
            messagebox.showinfo("成功", "退选成功！")
            self.load_courses()  # 刷新课程列表

        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"退选失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
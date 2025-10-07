import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class StudentList:
    def __init__(self, parent_frame, teacher_id):
        self.parent_frame = parent_frame
        self.teacher_id = teacher_id
        
        # 存储所有学生数据
        self.all_students = []
        
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
        ctk.CTkLabel(title_frame, text="选课名单", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主内容区域
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建左侧框架
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=10)

        # 课程选择区域
        course_frame = ctk.CTkFrame(left_frame)
        course_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择课程标题
        ctk.CTkLabel(course_frame, text="选择课程", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        self.course_var = tk.StringVar()
        self.course_combobox = ctk.CTkOptionMenu(course_frame, 
                                              variable=self.course_var,
                                              values=[],
                                              width=200,
                                              font=ctk.CTkFont(family="微软雅黑", size=12),
                                              fg_color="#4a90e2",
                                              button_color="#357abd",
                                              button_hover_color="#2980b9",
                                              dynamic_resizing=False,
                                              command=self.on_course_selected)
        self.course_combobox.pack(padx=5, pady=5)

        # 创建统计信息框架
        stats_frame = ctk.CTkFrame(left_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 统计信息标题
        ctk.CTkLabel(stats_frame, text="课程统计", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 统计信息标签
        self.total_label = ctk.CTkLabel(stats_frame, text="总人数：0",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
        self.total_label.pack(padx=5, pady=2)
        
        self.selected_label = ctk.CTkLabel(stats_frame, text="已选人数：0",
                                        font=ctk.CTkFont(family="微软雅黑", size=12))
        self.selected_label.pack(padx=5, pady=2)
        
        self.capacity_label = ctk.CTkLabel(stats_frame, text="课程容量：0",
                                        font=ctk.CTkFont(family="微软雅黑", size=12))
        self.capacity_label.pack(padx=5, pady=2)
        
        self.remaining_label = ctk.CTkLabel(stats_frame, text="剩余名额：0",
                                         font=ctk.CTkFont(family="微软雅黑", size=12))
        self.remaining_label.pack(padx=5, pady=2)

        # 创建学生列表框架
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 学生名单标题
        ctk.CTkLabel(list_frame, text="选课学生名单", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 创建学生列表的Treeview
        columns = ("学号", "姓名", "班级", "状态")
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15,
                                       style="Form.Treeview")
        
        # 设置列
        self.student_tree.column("学号", width=100)
        self.student_tree.column("姓名", width=100)
        self.student_tree.column("班级", width=150)
        self.student_tree.column("状态", width=100)
        
        for col in columns:
            self.student_tree.heading(col, text=col)

        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.student_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建右侧框架
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # 创建导出按钮
        ctk.CTkButton(right_frame, text="导出名单",
                    command=self.export_list,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#4a90e2",
                    hover_color="#357abd").pack(pady=20)

    def load_courses(self):
        """加载教师的课程列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 查询教师的课程
            cursor.execute("""
                SELECT id, name
                FROM courses
                WHERE teacher_id = %s
                ORDER BY name
            """, (self.teacher_id,))
            
            courses = cursor.fetchall()
            
            # 更新课程下拉框
            self.courses_data = {course[1]: course[0] for course in courses}
            course_names = list(self.courses_data.keys())
            self.course_combobox.configure(values=course_names)

            if courses:
                first_course = course_names[0]
                self.course_var.set(first_course)
                self.course_combobox.set(first_course)
                self.load_students(None)

        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def load_students(self, event):
        """加载选课学生列表"""
        if not self.course_var.get():
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            course_id = self.courses_data[self.course_var.get()]

            # 获取课程信息
            cursor.execute("""
                SELECT capacity
                FROM courses
                WHERE id = %s
            """, (course_id,))
            capacity = cursor.fetchone()[0]

            # 获取选课统计信息
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = '已选' THEN 1 ELSE 0 END) as selected
                FROM enrollments
                WHERE course_id = %s
            """, (course_id,))
            stats = cursor.fetchone()
            total = stats[0] or 0
            selected = stats[1] or 0

            # 更新统计信息
            self.total_label.configure(text=f"总人数：{total}")
            self.selected_label.configure(text=f"已选人数：{selected}")
            self.capacity_label.configure(text=f"课程容量：{capacity}")
            self.remaining_label.configure(text=f"剩余名额：{capacity - selected}")

            # 清空现有数据
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)

            # 查询选课学生
            sql = """
                SELECT 
                    s.id,
                    s.name,
                    c.name as class_name,
                    e.status
                FROM students s
                JOIN enrollments e ON s.id = e.student_id
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE e.course_id = %s
                ORDER BY e.status, s.id
            """
            cursor.execute(sql, (course_id,))
            students = cursor.fetchall()

            if not students:
                messagebox.showinfo("提示", "本课程暂无选课学生")

            # 缓存所有学生数据
            self.all_students = students

            # 显示学生列表
            self.refresh_student_tree(self.all_students)

        except Exception as e:
            messagebox.showerror("错误", f"加载学生列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def refresh_student_tree(self, students):
        # 清空现有数据
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        # 插入新数据
        for student in students:
            student_id, name, class_name, status = student
            self.student_tree.insert("", "end", values=(
                student_id,
                name,
                class_name if class_name else "-",
                status
            ))

    def export_list(self):
        """导出选课名单"""
        if not self.course_var.get():
            messagebox.showwarning("警告", "请先选择课程")
            return

        try:
            import csv
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{self.course_var.get()}_选课名单.csv"
            )
            
            if not file_path:
                return

            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 写入标题行
                writer.writerow(["学号", "姓名", "班级", "状态"])
                
                # 写入数据行
                for item in self.student_tree.get_children():
                    values = self.student_tree.item(item)['values']
                    if values:  # 确保有值
                        writer.writerow(values)

            messagebox.showinfo("成功", "选课名单导出成功")

        except Exception as e:
            messagebox.showerror("错误", f"导出名单失败：{str(e)}")

    def on_course_selected(self, choice):
        """当选择课程时加载学生列表"""
        self.load_students(None) 
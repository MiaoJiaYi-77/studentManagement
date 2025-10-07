import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles


class GradeEntry:
    def __init__(self, parent_frame, teacher_id):
        self.parent_frame = parent_frame
        self.teacher_id = teacher_id
        self.loading_courses = False  # 添加标志防止重复加载
        print(f"\n初始化成绩录入界面...")
        print(f"当前教师ID: {self.teacher_id}")
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        # 创建主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        self.title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(self.title_frame, text="成绩录入", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主内容区域
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建左侧课程选择框架
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 20), pady=10)

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
                                              dynamic_resizing=False)
        self.course_combobox.pack(padx=5, pady=5)
        self.course_combobox.bind('<Button-1>', self.on_course_selected)

        # 创建学生列表框架
        students_frame = ctk.CTkFrame(left_frame)
        students_frame.pack(fill=tk.BOTH, expand=True)
        
        # 学生名单标题
        ctk.CTkLabel(students_frame, text="学生名单", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 创建学生列表的Treeview
        columns = ("学号", "姓名", "成绩")
        self.student_tree = ttk.Treeview(students_frame, columns=columns, show="headings", height=15,
                                       style="Form.Treeview")

        # 设置列
        self.student_tree.column("学号", width=100)
        self.student_tree.column("姓名", width=100)
        self.student_tree.column("成绩", width=100)

        for col in columns:
            self.student_tree.heading(col, text=col)

        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(students_frame, command=self.student_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建右侧成绩录入框架
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        # 成绩录入表单
        grade_frame = ctk.CTkFrame(right_frame)
        grade_frame.pack(fill=tk.X, pady=(10, 20), padx=10)
        
        # 成绩录入标题
        ctk.CTkLabel(grade_frame, text="成绩录入", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=5)

        # 创建表单网格
        form_frame = ctk.CTkFrame(grade_frame, fg_color="transparent")
        form_frame.pack(pady=10)

        # 学生信息显示
        ctk.CTkLabel(form_frame, text="学号：", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.student_id_label = ctk.CTkLabel(form_frame, text="",
                                          font=ctk.CTkFont(family="微软雅黑", size=12))
        self.student_id_label.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        ctk.CTkLabel(form_frame, text="姓名：", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.student_name_label = ctk.CTkLabel(form_frame, text="",
                                            font=ctk.CTkFont(family="微软雅黑", size=12))
        self.student_name_label.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        ctk.CTkLabel(form_frame, text="成绩：", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=2, column=0, padx=5, pady=8, sticky="e")
        self.grade_var = tk.StringVar()
        self.grade_entry = ctk.CTkEntry(form_frame, textvariable=self.grade_var, width=100,
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
        self.grade_entry.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        # 绑定输入框内容变化事件
        self.grade_var.trace_add("write", self.on_grade_input_change)

        # 按钮框架
        button_frame = ctk.CTkFrame(grade_frame, fg_color="transparent")
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="保存成绩",
                    command=self.save_grade,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#4a90e2",
                    hover_color="#357abd").pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="清除输入",
                    command=self.clear_input,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#7f8c8d",
                    hover_color="#636e72").pack(side=tk.LEFT, padx=5)

        # 绑定学生选择事件
        self.student_tree.bind('<<TreeviewSelect>>', self.on_select_student)

    def load_courses(self):
        """加载教师的课程列表"""
        print(f"\n开始加载课程列表...")
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 查询教师的课程
            cursor.execute("""
                SELECT id, name, credit
                FROM courses
                WHERE teacher_id = %s
                ORDER BY name
            """, (self.teacher_id,))

            courses = cursor.fetchall()
            print(f"查询到 {len(courses)} 门课程")

            # 更新课程下拉框
            self.courses_data = {course[1]: course[0] for course in courses}
            course_names = list(self.courses_data.keys())
            self.course_combobox['values'] = course_names

            print("课程列表:")
            for course in courses:
                print(f"  - {course[1]} (ID: {course[0]}, 学分: {course[2]})")

            if courses:
                # 防止重复加载的标志
                self.loading_courses = True
                default_course = course_names[0]
                print(f"设置默认课程: {default_course}")

                # 先设置变量值，再设置下拉框的值
                self.course_var.set(default_course)
                self.course_combobox.set(default_course)

                # 直接调用加载学生列表方法，而不是通过事件
                print("手动触发加载学生列表...")
                print(f"当前选中的课程: {self.course_var.get()}")
                self.load_students(None)
                self.loading_courses = False
            else:
                print("没有找到任何课程")

        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
            print(f"加载课程列表失败：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()

    def load_students(self, event):
        """加载选择课程的学生列表"""
        selected_course = self.course_var.get()
        if not selected_course:
            print(f"未选择课程，无法加载学生列表 (course_var: '{selected_course}')")
            return

        print(f"\n开始加载学生列表...")
        print(f"当前选择的课程: '{selected_course}'")
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 保存当前选中的学生ID，以便重新加载后能重新选中
            selected_student_id = None
            selected_items = self.student_tree.selection()
            if selected_items:
                values = self.student_tree.item(selected_items[0], "values")
                if values:
                    selected_student_id = values[0]
                    print(f"当前选中的学生ID: {selected_student_id}")

            # 清空现有数据
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)

            if selected_course not in self.courses_data:
                print(f"错误：选中的课程'{selected_course}'不在课程字典中")
                print(f"可用课程: {list(self.courses_data.keys())}")
                return

            course_id = self.courses_data[selected_course]
            print(f"课程ID: {course_id}")

            # 查询选课学生及其成绩
            cursor.execute("""
                SELECT s.id, s.name, e.id as enrollment_id, sc.score
                FROM students s
                JOIN enrollments e ON s.id = e.student_id
                LEFT JOIN scores sc ON e.id = sc.enrollment_id
                WHERE e.course_id = %s AND e.status = '已选'
                ORDER BY s.id
            """, (course_id,))
            
            students = cursor.fetchall()
            print(f"查询到 {len(students)} 名学生")
            
            # 保存选课记录ID到字典中
            self.enrollment_ids = {}

            if not students:
                print("本课程暂无选课学生")
                messagebox.showinfo("提示", "本课程暂无选课学生")

            # 显示学生列表
            for student in students:
                student_id, name, enrollment_id, score = student
                self.enrollment_ids[student_id] = enrollment_id
                print(f"学生信息: ID={student_id}, 姓名={name}, 选课ID={enrollment_id}, 成绩={score if score is not None else '未录入'}")
                item_id = self.student_tree.insert("", "end", values=(
                    student_id,
                    name,
                    score if score is not None else "未录入"
                ))
                
                # 如果是之前选中的学生，重新选中
                if selected_student_id and str(student_id) == str(selected_student_id):
                    self.student_tree.selection_set(item_id)
                    self.student_tree.see(item_id)

            # 更新课程信息
            cursor.execute("""
                SELECT name, credit
                FROM courses
                WHERE id = %s
            """, (course_id,))
            
            course_info = cursor.fetchone()
            if course_info:
                course_name, credit = course_info
                print(f"课程详情: {course_name} ({credit}学分)")
                self.update_course_info(course_name, credit)

        except Exception as e:
            messagebox.showerror("错误", f"加载学生列表失败：{str(e)}")
            print(f"加载学生列表失败：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()
        # 自动清空右侧输入区
        self.grade_var.set("")
        self.student_id_label.configure(text="")
        self.student_name_label.configure(text="")

    def update_course_info(self, course_name, credit):
        """更新课程信息显示"""
        if hasattr(self, 'course_info_label'):
            self.course_info_label.destroy()

        self.course_info_label = ctk.CTkLabel(
            self.title_frame,  # 使用类成员变量
            text=f"当前课程：{course_name} ({credit}学分)",
            font=ctk.CTkFont(family="微软雅黑", size=14)
        )
        self.course_info_label.pack(side=tk.LEFT, padx=(20, 0))

    def on_select_student(self, event):
        """当选择学生时更新右侧信息"""
        selected_items = self.student_tree.selection()
        if not selected_items:
            return

        # 获取选中学生的信息
        values = self.student_tree.item(selected_items[0])['values']
        if values:
            student_id, name, score = values
            print(f"\n选中学生信息:")
            print(f"学号: {student_id}")
            print(f"姓名: {name}")
            print(f"当前成绩: {score}")

            self.student_id_label.configure(text=student_id)
            self.student_name_label.configure(text=name)
            # 如果成绩是数字，保持原样；如果是"未录入"，则清空输入框
            self.grade_var.set(score if score != "未录入" else "")

    def save_grade(self):
        """保存学生成绩"""
        print("\n开始保存成绩...")
        
        # 检查是否有选中的学生
        student_id = self.student_id_label.cget("text")
        if not student_id:
            print("未选择学生")
            messagebox.showwarning("警告", "请先选择一个学生")
            return
            
        # 检查成绩输入（直接从输入框控件获取最新内容）
        grade_input = self.grade_entry.get().strip()
        print(f"从输入框获取的成绩: '{grade_input}'")
        print(f"成绩变量值: {self.grade_var.get()}")
        print(f"输入框内容: {self.grade_entry.get()}")
        
        if not grade_input:
            print("成绩输入为空")
            messagebox.showwarning("警告", "请输入成绩")
            return
            
        try:
            grade = float(grade_input)
            if not (0 <= grade <= 100):
                print(f"成绩 {grade} 超出范围")
                messagebox.showwarning("警告", "成绩必须在0-100之间")
                return
        except ValueError:
            print(f"无效的成绩输入: {grade_input}")
            messagebox.showwarning("警告", "请输入有效的成绩")
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            selected_course = self.course_var.get()
            if not selected_course or selected_course not in self.courses_data:
                print(f"无效的课程选择: '{selected_course}'")
                messagebox.showerror("错误", "请选择有效的课程")
                return
                
            course_id = self.courses_data[selected_course]
            
            print(f"准备保存成绩:")
            print(f"学生ID: {student_id}")
            print(f"课程ID: {course_id}")
            print(f"成绩: {grade}")
            
            # 获取选课记录ID
            try:
                student_id_int = int(student_id)
                enrollment_id = self.enrollment_ids.get(student_id_int)
                print(f"从字典中获取选课记录ID: {enrollment_id} (学生ID: {student_id_int})")
                print(f"可用的选课记录: {self.enrollment_ids}")
            except (ValueError, TypeError):
                print(f"无效的学生ID: {student_id}")
                messagebox.showerror("错误", "无效的学生ID")
                return
                
            if not enrollment_id:
                # 尝试直接从数据库查询选课记录ID
                try:
                    print(f"从数据库查询选课记录...")
                    cursor.execute("""
                        SELECT id FROM enrollments 
                        WHERE student_id = %s AND course_id = %s AND status = '已选'
                    """, (student_id_int, course_id))
                    enrollment_result = cursor.fetchone()
                    if enrollment_result:
                        enrollment_id = enrollment_result[0]
                        print(f"从数据库查询到选课记录ID: {enrollment_id}")
                        # 更新字典，避免下次再查询
                        self.enrollment_ids[student_id_int] = enrollment_id
                    else:
                        print(f"数据库中没有找到选课记录")
                except Exception as db_error:
                    print(f"查询选课记录出错: {str(db_error)}")
            
            if not enrollment_id:
                print(f"找不到选课记录 (学生ID: {student_id}, 课程ID: {course_id})")
                messagebox.showerror("错误", "找不到选课记录")
                return

            print(f"选课记录ID: {enrollment_id}")

            # 检查成绩是否已存在
            cursor.execute("""
                SELECT id, score FROM scores
                WHERE enrollment_id = %s
            """, (enrollment_id,))
            
            existing_score = cursor.fetchone()

            if existing_score:
                score_id, old_score = existing_score
                print(f"更新现有成绩记录 (ID: {score_id}, 原成绩: {old_score} -> 新成绩: {grade})")
                # 更新成绩
                cursor.execute("""
                    UPDATE scores
                    SET score = %s
                    WHERE enrollment_id = %s
                """, (grade, enrollment_id))
                print(f"更新影响的行数: {cursor.rowcount}")
            else:
                print("添加新成绩记录")
                # 插入新成绩
                cursor.execute("""
                    INSERT INTO scores (enrollment_id, score, exam_time)
                    VALUES (%s, %s, CURDATE())
                """, (enrollment_id, grade))
                print(f"插入的记录ID: {cursor.lastrowid}")

            print("提交事务...")
            conn.commit()
            print("数据库操作已提交")
            
            # 立即更新界面显示的成绩
            for item in self.student_tree.get_children():
                values = self.student_tree.item(item, "values")
                if values and str(values[0]) == str(student_id):
                    print(f"更新界面显示: 学生{student_id}的成绩从{values[2]}更新为{grade}")
                    self.student_tree.set(item, 2, grade)  # 使用列索引而不是列名
                    self.student_tree.selection_set(item)
                    self.student_tree.see(item)
                    break
            
            # 清除成绩输入框内容，但保留学号和姓名
            self.grade_var.set("")
            
            messagebox.showinfo("成功", "成绩保存成功")

        except Exception as e:
            messagebox.showerror("错误", f"保存成绩失败：{str(e)}")
            print(f"保存成绩失败：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()

    def clear_input(self):
        """清除输入的成绩"""
        print("\n清除输入...")
        print("清除前的值:")
        print(f"学号: {self.student_id_label.cget('text')}")
        print(f"姓名: {self.student_name_label.cget('text')}")
        print(f"成绩: {self.grade_var.get()}")

        self.grade_var.set("")
        self.student_id_label.configure(text="")
        self.student_name_label.configure(text="")

        # 清除树形视图的选择
        for item in self.student_tree.selection():
            self.student_tree.selection_remove(item)

        print("输入已清除")

    def on_course_selected(self, event):
        """当选择课程时加载学生列表"""
        if not self.loading_courses:
            selected_course = self.course_var.get()
            print(f"用户选择了课程: '{selected_course}'")
            self.load_students(event)

    def on_grade_input_change(self, *args):
        """当成绩输入框内容变化时调用"""
        current_value = self.grade_var.get()
        print(f"成绩输入框内容变化: {current_value}")

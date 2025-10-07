import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class CourseSchedule:
    def __init__(self, parent_frame, teacher_id):
        self.parent_frame = parent_frame
        self.teacher_id = teacher_id
        self.courses_dict = {}  # 初始化课程字典
        self.loading_schedule = False  # 添加标志防止重复加载
        self.current_selected_id = None  # 添加选中ID变量
        print(f"当前教师ID: {self.teacher_id}")
        self.course_var = tk.StringVar()  # 初始化课程选择变量
        self.course_var.trace('w', self.on_course_change)  # 监听变量变化
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_courses()

    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.parent_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 左侧框架 - 课程选择
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # 课程选择
        course_select_frame = ttk.LabelFrame(left_frame, text="选择课程")
        course_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.course_combobox = ttk.Combobox(course_select_frame, textvariable=self.course_var, state="readonly", width=30)
        self.course_combobox.pack(padx=5, pady=5)
        # 使用直接绑定和trace双重保障
        self.course_combobox.bind('<<ComboboxSelected>>', self.on_combobox_select)

        # 显示现有安排的Treeview
        schedule_frame = ttk.LabelFrame(left_frame, text="现有安排")
        schedule_frame.pack(fill=tk.BOTH, expand=True)

        # 创建用于显示课程信息的标签（在load_schedules中动态更新）
        self.course_info_label = ttk.Label(schedule_frame, text="请选择一个课程")
        self.course_info_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=(5, 0))

        # 创建刷新按钮
        refresh_btn = ttk.Button(schedule_frame, text="刷新", command=lambda: self.load_schedules(None))
        refresh_btn.pack(side=tk.TOP, anchor=tk.E, padx=5, pady=(0, 5))

        # 创建Treeview和滚动条
        self.schedule_tree = ttk.Treeview(schedule_frame, 
                                        columns=("周次", "星期", "节次", "教室", "备注"),
                                        show="headings",
                                        height=15)

        # 设置列宽和标题
        self.schedule_tree.column("周次", width=100)
        self.schedule_tree.column("星期", width=80)
        self.schedule_tree.column("节次", width=60)
        self.schedule_tree.column("教室", width=100)
        self.schedule_tree.column("备注", width=150)

        self.schedule_tree.heading("周次", text="周次")
        self.schedule_tree.heading("星期", text="星期")
        self.schedule_tree.heading("节次", text="节次")
        self.schedule_tree.heading("教室", text="教室")
        self.schedule_tree.heading("备注", text="备注")

        # 设置不同星期的标签颜色
        self.schedule_tree.tag_configure("day_星期一", background="#F0F8FF")  # 浅蓝色
        self.schedule_tree.tag_configure("day_星期二", background="#F5F5DC")  # 米色
        self.schedule_tree.tag_configure("day_星期三", background="#F0FFF0")  # 浅绿色
        self.schedule_tree.tag_configure("day_星期四", background="#FFF0F5")  # 浅粉色
        self.schedule_tree.tag_configure("day_星期五", background="#F5F5F5")  # 浅灰色
        self.schedule_tree.tag_configure("day_星期六", background="#E6E6FA")  # 浅紫色
        self.schedule_tree.tag_configure("day_星期日", background="#FFE4E1")  # 浅红色

        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(schedule_frame, command=self.schedule_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 绑定选择事件
        self.schedule_tree.bind('<<TreeviewSelect>>', self.on_schedule_select)

        # 右侧框架 - 添加/编辑课程安排
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        # 添加/编辑标题
        ctk.CTkLabel(right_frame, text="添加/编辑课程安排", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=10)

        # 创建输入表单
        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # 周次
        week_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        week_frame.pack(fill=tk.X, pady=8)
        
        ctk.CTkLabel(week_frame, text="周次:", width=60, 
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.start_week = tk.StringVar()
        self.start_week_entry = ctk.CTkEntry(week_frame, textvariable=self.start_week, width=60,
                                          font=ctk.CTkFont(family="微软雅黑", size=12))
        self.start_week_entry.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(week_frame, text="至", 
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.end_week = tk.StringVar()
        self.end_week_entry = ctk.CTkEntry(week_frame, textvariable=self.end_week, width=60,
                                        font=ctk.CTkFont(family="微软雅黑", size=12))
        self.end_week_entry.pack(side=tk.LEFT, padx=5)

        # 星期
        weekday_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        weekday_frame.pack(fill=tk.X, pady=8)
        
        ctk.CTkLabel(weekday_frame, text="星期:", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.weekday = tk.StringVar()
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        self.weekday_combobox = ctk.CTkOptionMenu(weekday_frame, 
                                               variable=self.weekday,
                                               values=weekdays,
                                               width=120,
                                               font=ctk.CTkFont(family="微软雅黑", size=12),
                                               fg_color="#4a90e2",
                                               button_color="#357abd",
                                               button_hover_color="#2980b9")
        self.weekday_combobox.pack(side=tk.LEFT, padx=5)

        # 节次
        period_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        period_frame.pack(fill=tk.X, pady=8)
        
        ctk.CTkLabel(period_frame, text="节次:", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.period = tk.StringVar()
        self.period_entry = ctk.CTkEntry(period_frame, textvariable=self.period, width=60,
                                      font=ctk.CTkFont(family="微软雅黑", size=12))
        self.period_entry.pack(side=tk.LEFT, padx=5)

        # 教室
        classroom_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        classroom_frame.pack(fill=tk.X, pady=8)
        
        ctk.CTkLabel(classroom_frame, text="教室:", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.classroom = tk.StringVar()
        self.classroom_entry = ctk.CTkEntry(classroom_frame, textvariable=self.classroom, width=180,
                                         font=ctk.CTkFont(family="微软雅黑", size=12))
        self.classroom_entry.pack(side=tk.LEFT, padx=5)

        # 备注
        remark_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remark_frame.pack(fill=tk.X, pady=8)
        
        ctk.CTkLabel(remark_frame, text="备注:", width=60,
                   font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
        self.remark = tk.StringVar()
        self.remark_entry = ctk.CTkEntry(remark_frame, textvariable=self.remark, width=240,
                                      font=ctk.CTkFont(family="微软雅黑", size=12))
        self.remark_entry.pack(side=tk.LEFT, padx=5)

        # 按钮框架
        button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkButton(button_frame, text="保存", 
                    command=self.save_schedule,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#4a90e2",
                    hover_color="#357abd").pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="删除", 
                    command=self.delete_schedule,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#e74c3c",
                    hover_color="#c0392b").pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="清除", 
                    command=self.clear_form,
                    font=ctk.CTkFont(family="微软雅黑", size=12),
                    width=100,
                    height=32,
                    fg_color="#7f8c8d",
                    hover_color="#636e72").pack(side=tk.LEFT, padx=5)

    def load_courses(self):
        """加载教师的课程列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 验证教师ID
            cursor.execute("""
                SELECT t.id, t.name 
                FROM teachers t 
                JOIN users u ON t.id = u.id 
                WHERE t.id = %s AND u.role = '教师'
            """, (self.teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                messagebox.showerror("错误", f"未找到ID为{self.teacher_id}的教师信息")
                return
            
            print(f"教师信息: ID={teacher[0]}, 姓名={teacher[1]}")

            # 查询该教师的所有课程
            cursor.execute("""
                SELECT 
                    c.id, 
                    c.name, 
                    c.credit,
                    COUNT(DISTINCT cs.id) as schedule_count
                FROM courses c
                LEFT JOIN course_schedule cs ON c.id = cs.course_id
                WHERE c.teacher_id = %s
                GROUP BY c.id, c.name, c.credit
                ORDER BY c.name
            """, (self.teacher_id,))
            courses = cursor.fetchall()
            print(f"查询到的课程: {courses}")
            
            if not courses:
                messagebox.showinfo("提示", f"您（{teacher[1]}老师）暂时没有任何课程安排")
                self.course_combobox.configure(values=[])
                return

            # 只用课程名做key，保证和下拉框一致
            course_display = []
            self.courses_dict.clear()  # 清空现有课程字典
            for course in courses:
                course_id, name, credit, schedule_count = course
                self.courses_dict[name] = course_id
                course_display.append(name)
            
            self.course_combobox.configure(values=course_display)
            print(f"课程字典: {self.courses_dict}")
            print(f"下拉框选项: {course_display}")
            
            # 设置默认选中第一个课程
            if course_display:
                print(f"设置默认课程: {course_display[0]}")
                self.loading_schedule = True  # 设置加载标志
                self.course_var.set(course_display[0])
                print(f"当前course_var值: {self.course_var.get()}")
                self.parent_frame.after(100, self.load_schedules_wrapper)
                
        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
            print(f"错误详情：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def on_course_change(self, *args):
        """监听课程变化"""
        selected = self.course_var.get()
        print(f"课程变量变化: '{selected}'")
        if selected and not self.loading_schedule:
            self.loading_schedule = True
            self.parent_frame.after(100, self.load_schedules_wrapper)

    def load_schedules_wrapper(self):
        """包装load_schedules，处理加载状态"""
        try:
            self.load_schedules(None)
        finally:
            self.loading_schedule = False
            print("重置加载状态")

    def load_schedules(self, event):
        """加载课程安排"""
        selected_course = self.course_var.get()
        if event:  # 如果是事件触发，直接从combobox获取值
            selected_course = self.course_combobox.get()
            
        print(f"\n开始加载课程安排...")
        print(f"当前选中的课程: '{selected_course}'")
        print(f"课程字典状态: {self.courses_dict}")
        
        if not selected_course:
            print("无法加载课程安排：未选择课程")
            return
            
        if not self.courses_dict:
            print("无法加载课程安排：课程字典为空")
            return
            
        if selected_course not in self.courses_dict:
            print(f"错误：选中的课程'{selected_course}'不在课程字典中")
            print(f"可用课程: {list(self.courses_dict.keys())}")
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 清空现有显示
            for item in self.schedule_tree.get_children():
                self.schedule_tree.delete(item)
                
            course_id = int(self.courses_dict[selected_course])
            print(f"正在查询课程ID {course_id} 的安排")
            
            # 直接检查course_schedule表中的数据
            cursor.execute("""
                SELECT cs.id, cs.start_week, cs.end_week, cs.weekday, 
                       cs.class_period, cs.classroom, cs.remark
                FROM course_schedule cs
                WHERE cs.course_id = %s
                ORDER BY cs.start_week, 
                    FIELD(cs.weekday, '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'),
                    cs.class_period
            """, (course_id,))
            
            schedules = cursor.fetchall()
            print(f"查询到的课程安排: {schedules}")
            
            # 更新课程信息显示
            if hasattr(self, 'course_info_label'):
                # 不需要销毁，直接更新文本
                self.course_info_label.configure(text="请选择一个课程")
                
            # 获取课程详细信息
            cursor.execute("""
                SELECT c.name, c.credit, c.capacity 
                FROM courses c 
                WHERE c.id = %s
            """, (course_id,))
            
            course_info = cursor.fetchone()
            if course_info:
                name, credit, capacity = course_info
                info_text = f"当前课程: {name} ({credit}学分, 容量:{capacity}人)"
                self.course_info_label.configure(text=info_text)
            
            if not schedules:
                print(f"课程 {selected_course}（ID: {course_id}）暂无安排数据")
                self.schedule_tree.insert("", "end", 
                    values=("暂无课程安排", "", "", "", "请使用右侧表单添加")
                )
            else:
                print(f"开始插入{len(schedules)}条课程安排数据")
                for schedule in schedules:
                    schedule_id, start_week, end_week, weekday, period, classroom, remark = schedule
                    week_display = f"第{start_week}-{end_week}周"
                    period_display = f"第{period}节"
                    tag = f"day_{weekday}"
                    
                    try:
                        self.schedule_tree.insert("", "end", 
                            iid=schedule_id,
                            values=(
                                week_display,
                                weekday,
                                period_display,
                                classroom if classroom else "未指定",
                                remark if remark else ""
                            ),
                            tags=(tag,)
                        )
                        print(f"成功插入安排: {week_display} {weekday} {period_display}")
                    except Exception as e:
                        print(f"插入安排时出错: {str(e)}")
                
            # 设置不同星期的标签颜色
            self.schedule_tree.tag_configure("day_星期一", background="#F0F8FF")
            self.schedule_tree.tag_configure("day_星期二", background="#F5F5DC")
            self.schedule_tree.tag_configure("day_星期三", background="#F0FFF0")
            self.schedule_tree.tag_configure("day_星期四", background="#FFF0F5")
            self.schedule_tree.tag_configure("day_星期五", background="#F5F5F5")
            self.schedule_tree.tag_configure("day_星期六", background="#E6E6FA")
            self.schedule_tree.tag_configure("day_星期日", background="#FFE4E1")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载课程安排失败：{str(e)}")
            print(f"错误详情：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()

    def on_schedule_select(self, event):
        """处理选择课程安排事件"""
        selected_items = self.schedule_tree.selection()
        if not selected_items:
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            print(f"选中课程安排ID: {selected_items[0]}")
            # 存储当前选中的ID
            self.current_selected_id = selected_items[0]
            print(f"已保存当前选中ID: {self.current_selected_id}")
            
            cursor.execute("""
                SELECT cs.start_week, cs.end_week, cs.weekday, cs.class_period, cs.classroom, cs.remark, c.id, c.name
                FROM course_schedule cs
                JOIN courses c ON cs.course_id = c.id
                WHERE cs.id = %s
            """, (selected_items[0],))
            
            schedule = cursor.fetchone()
            if schedule:
                start_week, end_week, weekday, period, classroom, remark, course_id, course_name = schedule
                print(f"加载课程安排详情:")
                print(f"周次: {start_week}-{end_week}")
                print(f"星期: {weekday}")
                print(f"节次: {period}")
                print(f"教室: {classroom}")
                print(f"备注: {remark}")
                print(f"所属课程: {course_name} (ID: {course_id})")
                
                # 确保下拉框选择的是正确的课程
                if course_name in self.courses_dict:
                    self.course_var.set(course_name)
                    print(f"已切换到课程: {course_name}")
                
                # 设置表单值
                self.start_week.set(str(start_week))
                self.end_week.set(str(end_week))
                self.weekday.set(weekday)
                self.period.set(str(period))
                self.classroom.set(classroom or "")
                self.remark.set(remark or "")

                # 直接更新StringVar的值就可以了，不需要再手动删除和插入
                # customtkinter的组件会自动更新显示

        except Exception as e:
            messagebox.showerror("错误", f"加载课程安排详情失败：{str(e)}")
            print(f"加载详情失败：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()

    def validate_input(self):
        """验证输入数据"""
        try:
            if not self.start_week.get() or not self.end_week.get() or not self.period.get():
                messagebox.showwarning("警告", "请填写完整的课程安排信息")
                return False
                
            start_week = int(self.start_week.get())
            end_week = int(self.end_week.get())
            period = int(self.period.get())

            if not (1 <= start_week <= 20 and 1 <= end_week <= 20):
                messagebox.showwarning("警告", "周次必须在1-20周之间")
                return False

            if start_week > end_week:
                messagebox.showwarning("警告", "起始周不能大于结束周")
                return False

            if not (1 <= period <= 12):
                messagebox.showwarning("警告", "节次必须在1-12节之间")
                return False

            if not self.weekday.get():
                messagebox.showwarning("警告", "请选择星期")
                return False

            if not self.classroom.get().strip():
                messagebox.showwarning("警告", "请输入教室")
                return False

            return True

        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
            return False

    def save_schedule(self):
        """保存课程安排"""
        print("\n开始保存课程安排...")
        print(f"当前表单值:")
        print(f"开始周: {self.start_week_entry.get()}")
        print(f"结束周: {self.end_week_entry.get()}")
        print(f"星期: {self.weekday_combobox.get()}")
        print(f"节次: {self.period_entry.get()}")
        print(f"教室: {self.classroom_entry.get()}")
        print(f"备注: {self.remark_entry.get()}")
        print(f"当前选中ID: {self.current_selected_id}")

        # 更新StringVar的值
        self.start_week.set(self.start_week_entry.get())
        self.end_week.set(self.end_week_entry.get())
        self.weekday.set(self.weekday_combobox.get())
        self.period.set(self.period_entry.get())
        self.classroom.set(self.classroom_entry.get())
        self.remark.set(self.remark_entry.get())

        if not self.validate_input():
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor(buffered=True)

            selected_course = self.course_var.get()
            if not selected_course:
                messagebox.showwarning("警告", "请先选择课程")
                return
                
            if selected_course not in self.courses_dict:
                messagebox.showerror("错误", "无效的课程选择")
                return
                
            course_id = self.courses_dict[selected_course]
            start_week = int(self.start_week.get())
            end_week = int(self.end_week.get())
            period = int(self.period.get())
            weekday = self.weekday.get()
            classroom = self.classroom.get().strip()
            remark = self.remark.get().strip()
            
            # 使用保存的选中ID，而不是当前树的选择
            is_editing = self.current_selected_id is not None
            
            print(f"\n准备保存的数据:")
            print(f"课程: {selected_course} (ID: {course_id})")
            print(f"周次: {start_week}-{end_week}")
            print(f"星期: {weekday}")
            print(f"节次: {period}")
            print(f"教室: {classroom}")
            print(f"备注: {remark}")
            print(f"是否编辑模式: {is_editing}")
            if is_editing:
                print(f"编辑现有安排ID: {self.current_selected_id}")

            # 检查时间冲突
            conflict_check_sql = """
                SELECT cs.id, c.name, cs.weekday, cs.class_period, cs.classroom
                FROM course_schedule cs
                JOIN courses c ON cs.course_id = c.id
                WHERE cs.weekday = %s 
                AND cs.class_period = %s
                AND cs.classroom = %s
                AND (
                    (cs.start_week BETWEEN %s AND %s)
                    OR (cs.end_week BETWEEN %s AND %s)
                    OR (%s BETWEEN cs.start_week AND cs.end_week)
                )
            """
            
            # 如果是编辑模式，排除当前记录
            if is_editing:
                conflict_check_sql += " AND cs.id != %s"
                cursor.execute(conflict_check_sql, (
                    weekday, period, classroom,
                    start_week, end_week,
                    start_week, end_week,
                    start_week,
                    self.current_selected_id
                ))
            else:
                cursor.execute(conflict_check_sql, (
                    weekday, period, classroom,
                    start_week, end_week,
                    start_week, end_week,
                    start_week
                ))
            
            conflict = cursor.fetchone()
            if conflict:
                conflict_id, conflict_name, conflict_day, conflict_period, conflict_room = conflict
                error_msg = f"时间冲突：\n课程：{conflict_name}\n时间：{conflict_day}第{conflict_period}节\n教室：{conflict_room}"
                messagebox.showwarning("警告", error_msg)
                return

            # 根据是否有选中项来决定是更新还是插入
            if is_editing:
                schedule_id = self.current_selected_id
                print(f"更新现有安排 ID: {schedule_id}")
                
                # 验证要更新的记录是否存在
                cursor.execute("SELECT id FROM course_schedule WHERE id = %s", (schedule_id,))
                if not cursor.fetchone():
                    messagebox.showerror("错误", "要更新的课程安排不存在")
                    return
                
                # 更新现有安排
                update_sql = """
                    UPDATE course_schedule 
                    SET course_id = %s, start_week = %s, end_week = %s,
                        weekday = %s, class_period = %s,
                        classroom = %s, remark = %s
                    WHERE id = %s
                """
                params = (
                    course_id, start_week, end_week,
                    weekday, period,
                    classroom, remark,
                    schedule_id
                )
                print(f"执行更新SQL: {update_sql}")
                print(f"参数: {params}")
                
                cursor.execute(update_sql, params)
                affected_rows = cursor.rowcount
                print(f"更新影响的行数: {affected_rows}")
                
                if affected_rows == 0:
                    messagebox.showerror("错误", "更新失败，请刷新后重试")
                    return
                    
                # 验证更新是否成功
                cursor.execute("SELECT * FROM course_schedule WHERE id = %s", (schedule_id,))
                updated_data = cursor.fetchone()
                if updated_data:
                    print(f"更新后数据: {updated_data}")
                else:
                    print(f"警告: 无法获取更新后的数据")
                    
            else:
                print("添加新课程安排")
                # 添加新安排
                insert_sql = """
                    INSERT INTO course_schedule (
                        course_id, start_week, end_week,
                        weekday, class_period, classroom, remark
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    course_id, start_week, end_week,
                    weekday, period,
                    classroom, remark
                )
                print(f"执行插入SQL: {insert_sql}")
                print(f"参数: {params}")
                
                cursor.execute(insert_sql, params)
                affected_rows = cursor.rowcount
                print(f"插入影响的行数: {affected_rows}")
                last_id = cursor.lastrowid
                print(f"新插入的ID: {last_id}")
                
                if affected_rows == 0:
                    messagebox.showerror("错误", "添加失败，请重试")
                    return
                    
                # 验证插入是否成功
                if last_id:
                    cursor.execute("SELECT * FROM course_schedule WHERE id = %s", (last_id,))
                    inserted_data = cursor.fetchone()
                    if inserted_data:
                        print(f"插入后数据: {inserted_data}")
                    else:
                        print(f"警告: 无法获取插入后的数据")

            print("提交事务...")
            conn.commit()
            print("数据库操作已提交")
            
            # 显示成功消息
            operation = "更新" if is_editing else "添加"
            messagebox.showinfo("成功", f"课程安排{operation}成功")
            
            # 重新加载显示
            self.load_schedules(None)
            # 清除表单和选中状态
            self.clear_form()

        except Exception as e:
            messagebox.showerror("错误", f"保存课程安排失败：{str(e)}")
            print(f"保存失败：{str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_schedule(self):
        """删除课程安排"""
        selected_items = self.schedule_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的课程安排")
            return

        if not messagebox.askyesno("确认", "确定要删除选中的课程安排吗？"):
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            cursor.execute("DELETE FROM course_schedule WHERE id = %s", (selected_items[0],))
            conn.commit()

            messagebox.showinfo("成功", "课程安排删除成功")
            self.load_schedules(None)
            self.clear_form()

        except Exception as e:
            messagebox.showerror("错误", f"删除课程安排失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def clear_form(self):
        """清除表单"""
        print("清除表单...")
        # 清除StringVar的值即可
        self.start_week.set("")
        self.end_week.set("")
        self.weekday.set("")
        self.period.set("")
        self.classroom.set("")
        self.remark.set("")
        
        # 清除选中状态
        for item in self.schedule_tree.selection():
            self.schedule_tree.selection_remove(item)
            
        # 重置当前选中ID
        self.current_selected_id = None
        print("当前选中ID已重置")
        
        print("表单已清除")

    def on_combobox_select(self, event):
        """直接处理下拉框选择事件"""
        selected = self.course_combobox.get()
        print(f"下拉框选择: '{selected}'")
        if selected and not self.loading_schedule:
            self.loading_schedule = True
            self.load_schedules(event)
            self.loading_schedule = False 
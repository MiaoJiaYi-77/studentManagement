import tkinter as tk
import customtkinter as ctk
from mysql.connector import Error
import mysql.connector

from admin.class_management import ClassManagement
from admin.course_management import CourseManagement
from admin.enrollment_management import EnrollmentManagement
from admin.score_management import ScoreManagement
from admin.teacher_management import TeacherManagement
from db_config import DatabaseConfig
from admin.user_management import UserManagement
from admin.student_management import StudentManagement
from admin.notice_management import NoticeManagement
from student.personal_info import PersonalInfo

# 设置默认外观模式和颜色主题
ctk.set_appearance_mode("light")  # 模式: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # 主题: "blue", "green", "dark-blue"

class MainWindow:
    def __init__(self, user_id, role, master):
        self.user_id = user_id
        self.role = role
        self.master = master
        
        # 创建主窗口（Toplevel）
        self.root = ctk.CTkToplevel(master)
        self.root.title(f"学生管理系统 - {role}界面")
        
        # 设置窗口大小
        self.root.geometry("1200x700")
        
        # 等待窗口创建完成后再设置位置
        self.root.after(10, self.center_window)
        
        # 设置自定义颜色方案
        self.setup_colors()

        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建左侧菜单和右侧内容区域
        self.create_widgets()

    def center_window(self):
        """将窗口居中显示"""
        window_width = 1200
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.lift()
        self.root.focus_force()

    def setup_colors(self):
        """设置自定义颜色方案"""
        self.colors = {
            'primary': "#1e88e5",      # 主要颜色
            'primary_hover': "#1976d2", # 主要颜色悬停
            'primary_pressed': "#1565c0", # 主要颜色按下
            'secondary': "#f5f5f5",     # 次要颜色
            'secondary_text': "#424242", # 次要文字颜色
            'success': "#4caf50",       # 成功颜色
            'warning': "#ff9800",       # 警告颜色
            'danger': "#f44336",        # 危险颜色
            'text': "#212121",          # 文字颜色
            'text_secondary': "#757575" # 次要文字颜色
        }

    def create_widgets(self):
        # 创建左侧菜单栏
        menu_frame = ctk.CTkFrame(self.main_frame, width=220, corner_radius=10)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        menu_frame.pack_propagate(False)

        # 创建右侧内容区域
        content_container = ctk.CTkFrame(self.main_frame, corner_radius=10)
        content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 设置内容框架
        self.content_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 根据角色创建不同的菜单
        if self.role == '学生':
            self.create_student_menu(menu_frame)
        elif self.role == '教师':
            self.create_teacher_menu(menu_frame)
        elif self.role == '管理员':
            self.create_admin_menu(menu_frame)

        # 默认显示欢迎页面
        self.show_welcome_page()

    def create_student_menu(self, menu_frame):
        # 添加系统名称
        ctk.CTkLabel(menu_frame, text="学生管理系统", 
                    font=ctk.CTkFont(family="微软雅黑", size=18, weight="bold")).pack(pady=20)
        
        # 添加功能按钮
        ctk.CTkButton(menu_frame, text="个人信息", 
                     command=self.show_personal_info,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="课程选择", 
                     command=self.show_course_selection,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="成绩查询", 
                     command=self.show_grades,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="考勤信息", 
                     command=self.show_attendance,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="奖惩记录", 
                     command=self.show_rewards_punishments,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="公告通知", 
                     command=self.show_notices,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
        
        # 退出按钮放在底部
        ctk.CTkButton(menu_frame, text="退出登录", 
                     command=self.logout,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color=self.colors['danger'],
                     hover_color="#d32f2f",
                     height=36).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

    def create_teacher_menu(self, menu_frame):
        # 添加系统名称
        ctk.CTkLabel(menu_frame, text="学生管理系统", 
                    font=ctk.CTkFont(family="微软雅黑", size=18, weight="bold")).pack(pady=20)
        
        # 添加功能按钮
        ctk.CTkButton(menu_frame, text="课程信息", 
                     command=self.show_course_info,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="成绩录入", 
                     command=self.show_grade_entry,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="课程安排", 
                     command=self.show_course_schedule,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="选课名单", 
                     command=self.show_student_list,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="发布公告", 
                     command=self.show_notice_publish,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
        
        # 退出按钮放在底部
        ctk.CTkButton(menu_frame, text="退出登录", 
                     command=self.logout,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color=self.colors['danger'],
                     hover_color="#d32f2f",
                     height=36).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

    def create_admin_menu(self, menu_frame):
        # 添加系统名称
        ctk.CTkLabel(menu_frame, text="学生管理系统", 
                    font=ctk.CTkFont(family="微软雅黑", size=18, weight="bold")).pack(pady=20)
        
        # 添加功能按钮
        ctk.CTkButton(menu_frame, text="用户管理", 
                     command=self.show_user_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="学生管理", 
                     command=self.show_student_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="教师管理", 
                     command=self.show_teacher_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="班级管理", 
                     command=self.show_class_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="课程管理", 
                     command=self.show_course_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="选课管理", 
                     command=self.show_enrollment_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="成绩管理", 
                     command=self.show_grade_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="公告管理", 
                     command=self.show_notice_management,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
                     
        ctk.CTkButton(menu_frame, text="数据分析", 
                     command=self.show_data_analysis,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     height=36).pack(fill=tk.X, padx=10, pady=5)
        
        # 退出按钮放在底部
        ctk.CTkButton(menu_frame, text="退出登录", 
                     command=self.logout,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color=self.colors['danger'],
                     hover_color="#d32f2f",
                     height=36).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

    def show_welcome_page(self):
        """显示欢迎页面"""
        self.clear_content_frame()
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_frame.pack(expand=True)
        
        # 创建欢迎标题
        ctk.CTkLabel(welcome_frame, 
                    text="欢迎使用学生管理系统",
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(pady=30)
        
        ctk.CTkLabel(welcome_frame, 
                    text=f"当前用户角色：{self.role}",
                    font=ctk.CTkFont(family="微软雅黑", size=14)).pack(pady=15)
        
        # 获取用户信息
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            if self.role == '学生':
                cursor.execute("SELECT name FROM students WHERE id = %s", (self.user_id,))
            elif self.role == '教师':
                cursor.execute("SELECT name FROM teachers WHERE id = %s", (self.user_id,))
            else:
                cursor.execute("SELECT username FROM users WHERE id = %s", (self.user_id,))
                
            result = cursor.fetchone()
            if result:
                ctk.CTkLabel(welcome_frame, 
                           text=f"用户名：{result[0]}",
                           font=ctk.CTkFont(family="微软雅黑", size=14)).pack(pady=10)
                
        except Error as e:
            from tkinter import messagebox
            messagebox.showerror("错误", f"获取用户信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
        # 添加版本信息
        version_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        version_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        ctk.CTkLabel(version_frame, 
                    text="学生管理系统 v1.0.0",
                    font=ctk.CTkFont(family="微软雅黑", size=10),
                    text_color=self.colors['text_secondary']).pack(side=tk.RIGHT)

    def clear_content_frame(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_personal_info(self):
        """显示个人信息"""
        self.clear_content_frame()
        # 创建一个框架来容纳个人信息
        info_container = ctk.CTkFrame(self.content_frame)
        info_container.pack(fill=tk.BOTH, expand=True)
        # 初始化个人信息页面
        PersonalInfo(info_container, self.user_id)

    def show_course_selection(self):
        """显示课程选择"""
        self.clear_content_frame()
        # 创建一个框架来容纳课程选择
        selection_container = ctk.CTkFrame(self.content_frame)
        selection_container.pack(fill=tk.BOTH, expand=True)
        # 初始化课程选择页面
        from student.course_selection import CourseSelection
        CourseSelection(selection_container, self.user_id)

    def show_grades(self):
        """显示成绩查询"""
        self.clear_content_frame()
        # 创建一个框架来容纳成绩查询
        grades_container = ctk.CTkFrame(self.content_frame)
        grades_container.pack(fill=tk.BOTH, expand=True)
        # 初始化成绩查询页面
        from student.grade_query import GradeQuery
        GradeQuery(grades_container, self.user_id)

    def show_attendance(self):
        """显示考勤信息"""
        self.clear_content_frame()
        # 创建一个框架来容纳考勤信息
        attendance_container = ctk.CTkFrame(self.content_frame)
        attendance_container.pack(fill=tk.BOTH, expand=True)
        # 初始化考勤信息页面
        from student.attendance_query import AttendanceQuery
        AttendanceQuery(attendance_container, self.user_id)

    def show_rewards_punishments(self):
        """显示奖惩记录"""
        self.clear_content_frame()
        # 创建一个框架来容纳奖惩记录
        rewards_punishments_container = ctk.CTkFrame(self.content_frame)
        rewards_punishments_container.pack(fill=tk.BOTH, expand=True)
        # 初始化奖惩记录页面
        from student.rewards_punishments_query import RewardsPunishmentsQuery
        RewardsPunishmentsQuery(rewards_punishments_container, self.user_id)

    def show_notices(self):
        """显示公告通知"""
        self.clear_content_frame()
        # 创建一个框架来容纳公告通知
        notices_container = ctk.CTkFrame(self.content_frame)
        notices_container.pack(fill=tk.BOTH, expand=True)
        # 初始化公告通知页面
        from student.notice_view import NoticeView
        NoticeView(notices_container)

    def show_course_info(self):
        """显示课程信息"""
        self.clear_content_frame()
        # 创建一个框架来容纳课程信息
        course_info_container = ctk.CTkFrame(self.content_frame)
        course_info_container.pack(fill=tk.BOTH, expand=True)
        # 初始化课程信息页面
        from teacher.course_info import CourseInfo
        CourseInfo(course_info_container, self.user_id)

    def show_grade_entry(self):
        self.clear_content_frame()
        # 创建一个框架来容纳成绩录入
        grade_entry_container = ctk.CTkFrame(self.content_frame)
        grade_entry_container.pack(fill=tk.BOTH, expand=True)
        # 初始化成绩录入页面
        from teacher.grade_entry import GradeEntry
        GradeEntry(grade_entry_container, self.user_id)

    def show_course_schedule(self):
        self.clear_content_frame()
        # 创建一个框架来容纳课程安排
        schedule_container = ctk.CTkFrame(self.content_frame)
        schedule_container.pack(fill=tk.BOTH, expand=True)
        # 初始化课程安排页面
        from teacher.course_schedule import CourseSchedule
        CourseSchedule(schedule_container, self.user_id)

    def show_student_list(self):
        self.clear_content_frame()
        # 创建一个框架来容纳选课名单
        student_list_container = ctk.CTkFrame(self.content_frame)
        student_list_container.pack(fill=tk.BOTH, expand=True)
        # 初始化选课名单页面
        from teacher.student_list import StudentList
        StudentList(student_list_container, self.user_id)

    def show_notice_publish(self):
        """显示通知公告管理"""
        self.clear_content_frame()
        NoticeManagement(self.content_frame, self.user_id)

    def show_user_management(self):
        """显示用户管理界面"""
        self.clear_content_frame()
        UserManagement(self.content_frame)

    def show_student_management(self):
        self.clear_content_frame()
        StudentManagement(self.content_frame)

    def show_teacher_management(self):
        self.clear_content_frame()
        TeacherManagement(self.content_frame)

    def show_class_management(self):
        self.clear_content_frame()
        ClassManagement(self.content_frame)

    def show_course_management(self):
        self.clear_content_frame()
        CourseManagement(self.content_frame)

    def show_enrollment_management(self):
        self.clear_content_frame()
        EnrollmentManagement(self.content_frame)

    def show_grade_management(self):
        self.clear_content_frame()
        ScoreManagement(self.content_frame)

    def show_notice_management(self):
        """显示通知公告管理"""
        self.clear_content_frame()
        NoticeManagement(self.content_frame, self.user_id)

    def show_data_analysis(self):
        """显示数据分析界面"""
        self.clear_content_frame()
        # 创建一个框架来容纳数据分析
        analysis_container = ctk.CTkFrame(self.content_frame)
        analysis_container.pack(fill=tk.BOTH, expand=True)
        # 初始化数据分析页面
        from admin.data_analysis.main_analysis import DataAnalysisModule
        DataAnalysisModule(analysis_container)

    def logout(self):
        """退出登录"""
        from tkinter import messagebox
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            # 通知主窗口显示登录界面
            self.root.destroy()
            self.master.deiconify()

    def run(self):
        """运行主窗口"""
        self.root.mainloop() 
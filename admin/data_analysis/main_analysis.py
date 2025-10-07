import tkinter as tk
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from mysql.connector import Error
import mysql.connector
from db_config import DatabaseConfig
import matplotlib.pyplot as plt
from matplotlib import font_manager

class DataAnalysisModule:
    def __init__(self, parent):
        self.parent = parent
        # 设置matplotlib的全局字体
        plt.rcParams['font.family'] = 'Microsoft YaHei'
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主布局
        self.create_main_layout()
        # 创建控制面板
        self.create_control_panel()
        # 创建图表区域
        self.create_chart_area()
        
    def create_main_layout(self):
        # 左侧控制面板
        self.control_frame = ctk.CTkFrame(self.parent, width=200)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        
        # 右侧图表区域
        self.chart_container = ctk.CTkFrame(self.parent)
        self.chart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_control_panel(self):
        # 分析类型选择
        ctk.CTkLabel(self.control_frame, text="分析类型", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(20,10))
        
        analysis_types = [
            "成绩趋势分析",
            "考勤比例分析",
            "课程选择分析"
        ]
        
        self.analysis_var = tk.StringVar(value=analysis_types[0])
        for analysis_type in analysis_types:
            ctk.CTkRadioButton(self.control_frame, text=analysis_type,
                             variable=self.analysis_var,
                             value=analysis_type,
                             command=self.on_analysis_type_change,
                             font=ctk.CTkFont(family="微软雅黑")).pack(pady=5, padx=20, anchor="w")
        
        # 时间范围选择
        ctk.CTkLabel(self.control_frame, text="时间范围", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(20,10))
        
        time_ranges = [
            "本学期",
            "上学期",
            "本学年",
            "全部"
        ]
        
        self.time_var = tk.StringVar(value=time_ranges[0])
        for time_range in time_ranges:
            ctk.CTkRadioButton(self.control_frame, text=time_range,
                             variable=self.time_var,
                             value=time_range,
                             command=self.on_time_range_change,
                             font=ctk.CTkFont(family="微软雅黑")).pack(pady=5, padx=20, anchor="w")
        
        # 更新按钮
        ctk.CTkButton(self.control_frame, text="更新图表",
                     command=self.update_chart,
                     font=ctk.CTkFont(family="微软雅黑")).pack(pady=20)
        
    def create_chart_area(self):
        # 创建图表标题
        self.chart_title = ctk.CTkLabel(self.chart_container, text="数据分析图表",
                                      font=ctk.CTkFont(family="微软雅黑", size=16, weight="bold"))
        self.chart_title.pack(pady=10)
        
        # 创建图表框架，使用pack布局管理器实现居中
        self.chart_frame = ctk.CTkFrame(self.chart_container)
        self.chart_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # 初始化默认图表
        self.current_canvas = None
        self.update_chart()
        
    def on_analysis_type_change(self):
        self.update_chart()
        
    def on_time_range_change(self):
        self.update_chart()
        
    def update_chart(self):
        # 清除现有图表
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            
        analysis_type = self.analysis_var.get()
        time_range = self.time_var.get()
        
        # 根据选择的分析类型调用相应的数据处理和绘图函数
        if analysis_type == "成绩趋势分析":
            self.show_grade_trends()
        elif analysis_type == "考勤比例分析":
            self.show_attendance_pie()
        elif analysis_type == "课程选择分析":
            self.show_course_enrollment_bar()
            
    def show_grade_trends(self):
        """柱状图：展示成绩趋势"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 查询各科目平均分
            cursor.execute("""
                SELECT c.name as course_name, 
                       AVG(s.score) as avg_score
                FROM scores s
                JOIN enrollments e ON s.enrollment_id = e.id
                JOIN courses c ON e.course_id = c.id
                GROUP BY c.name
                ORDER BY avg_score DESC
            """)
            
            data = cursor.fetchall()
            courses = [row[0] for row in data]
            scores = [row[1] for row in data]
            
            # 创建图表
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # 设置背景
            ax.set_facecolor('#f8f9fa')
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 创建渐变色
            gradient_colors = []
            for i in range(len(courses)):
                # 使用蓝色到紫色的渐变
                gradient_colors.append(plt.cm.cool(i / len(courses)))
            
            # 绘制柱状图
            bars = ax.bar(courses, scores, color=gradient_colors)
            
            # 为每个柱子添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom',
                       font="Microsoft YaHei",
                       fontsize=10)
            
            # 设置标题和标签
            ax.set_title('各科目平均分对比', 
                        fontproperties="Microsoft YaHei", 
                        fontsize=14,
                        pad=20)
            ax.set_xlabel('课程名称', fontproperties="Microsoft YaHei", fontsize=12)
            ax.set_ylabel('平均分', fontproperties="Microsoft YaHei", fontsize=12)
            
            # 设置y轴范围
            ax.set_ylim(0, 100)
            
            # 设置刻度标签
            plt.setp(ax.get_xticklabels(), 
                    rotation=45, 
                    ha='right', 
                    font="Microsoft YaHei",
                    fontsize=10)
            
            # 移除顶部和右侧边框
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # 调整布局
            fig.tight_layout()
            
            # 显示图表
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True)
            self.current_canvas = canvas
            
        except Error as e:
            print(f"数据库错误：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
    def show_attendance_pie(self):
        """饼图：展示考勤情况比例"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 查询考勤状态的分布
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM attendance
                GROUP BY status
            """)
            
            data = cursor.fetchall()
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            
            # 创建图表
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # 设置新的颜色方案
            colors = {
                '出勤': '#3498db',  # 蓝色
                '迟到': '#f39c12',  # 橙色
                '缺勤': '#9b59b6',  # 紫色
                '请假': '#1abc9c'   # 青色
            }
            
            # 绘制饼图
            wedges, texts, autotexts = ax.pie(sizes, 
                                            labels=labels, 
                                            autopct='%1.1f%%',
                                            colors=[colors.get(label, '#95a5a6') for label in labels],
                                            startangle=90)
            
            # 设置标题
            ax.set_title('学生考勤情况分布', 
                        fontproperties="Microsoft YaHei", 
                        fontsize=14,
                        pad=20)
            
            # 设置图例字体
            plt.setp(texts, font="Microsoft YaHei", fontsize=10)
            plt.setp(autotexts, font="Microsoft YaHei", fontsize=10)
            
            # 添加图例
            ax.legend(wedges, labels,
                     title="考勤状态",
                     loc="center left",
                     bbox_to_anchor=(1, 0, 0.5, 1),
                     prop={'family': 'Microsoft YaHei', 'size': 10})
            
            # 调整布局
            fig.tight_layout()
            
            # 显示图表
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True)
            self.current_canvas = canvas
            
        except Error as e:
            print(f"数据库错误：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
    def show_course_enrollment_bar(self):
        """柱状图：展示课程选择人数对比"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 查询各课程的选课人数
            cursor.execute("""
                SELECT c.name as course_name, 
                       COUNT(e.student_id) as enrollment_count
                FROM courses c
                LEFT JOIN enrollments e ON c.id = e.course_id
                WHERE e.status = '已选'
                GROUP BY c.id, c.name
                ORDER BY enrollment_count DESC
                LIMIT 10
            """)
            
            data = cursor.fetchall()
            courses = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            # 创建图表
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # 设置背景
            ax.set_facecolor('#f8f9fa')
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 创建渐变色
            gradient_colors = []
            for i in range(len(courses)):
                # 使用HSV颜色空间创建渐变效果
                hue = 0.6 - (i * 0.5 / len(courses))  # 从蓝色到紫色的渐变
                gradient_colors.append(plt.cm.viridis(i / len(courses)))
            
            # 绘制柱状图
            bars = ax.bar(courses, counts, color=gradient_colors)
            
            # 为每个柱子添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom',
                       font="Microsoft YaHei",
                       fontsize=10)
            
            # 设置标题和标签
            ax.set_title('课程选课人数对比（Top 10）', 
                        fontproperties="Microsoft YaHei", 
                        fontsize=14,
                        pad=20)
            ax.set_xlabel('课程名称', fontproperties="Microsoft YaHei", fontsize=12)
            ax.set_ylabel('选课人数', fontproperties="Microsoft YaHei", fontsize=12)
            
            # 设置刻度标签
            plt.setp(ax.get_xticklabels(), 
                    rotation=45, 
                    ha='right', 
                    font="Microsoft YaHei",
                    fontsize=10)
            
            # 移除顶部和右侧边框
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # 调整布局
            fig.tight_layout()
            
            # 显示图表
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True)
            self.current_canvas = canvas
            
        except Error as e:
            print(f"数据库错误：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
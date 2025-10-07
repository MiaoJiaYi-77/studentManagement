import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from styles.form_styles import apply_form_styles

class GradeQuery:
    def __init__(self, parent_frame, student_id):
        self.parent_frame = parent_frame
        self.student_id = student_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_grades()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="成绩查询", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建成绩列表
        columns = ("课程名称", "教师", "学分", "成绩", "考试时间")
        self.grade_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                     style="Form.Treeview")
        
        # 设置列宽和标题
        self.grade_tree.column("课程名称", width=200)
        self.grade_tree.column("教师", width=150)
        self.grade_tree.column("学分", width=100)
        self.grade_tree.column("成绩", width=100)
        self.grade_tree.column("考试时间", width=150)
        
        for col in columns:
            self.grade_tree.heading(col, text=col)

        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.grade_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.grade_tree.configure(yscrollcommand=scrollbar.set)
        self.grade_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建统计信息框架
        stats_frame = ctk.CTkFrame(self.frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 统计标题
        ctk.CTkLabel(stats_frame, text="统计信息", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(5, 10))

        # 统计信息标签
        self.stats_labels = {}
        stats_items = [
            ("total_credit", "总学分："),
            ("avg_score", "平均分："),
            ("pass_rate", "通过率："),
            ("highest_score", "最高分："),
            ("lowest_score", "最低分：")
        ]

        # 创建统计信息网格
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=5)
        
        for i, (key, text) in enumerate(stats_items):
            # 标签
            ctk.CTkLabel(stats_grid, text=text,
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=i//3, column=(i%3)*2, padx=15, pady=10, sticky="e")
            # 值
            value_label = ctk.CTkLabel(stats_grid, text="--",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
            value_label.grid(row=i//3, column=(i%3)*2+1, padx=15, pady=10, sticky="w")
            self.stats_labels[key] = value_label

    def load_grades(self):
        """加载成绩信息"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.grade_tree.get_children():
                self.grade_tree.delete(item)

            # 查询成绩信息
            cursor.execute("""
                SELECT 
                    c.name as course_name,
                    t.name as teacher_name,
                    c.credit,
                    s.score,
                    s.exam_time
                FROM enrollments e
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN scores s ON e.id = s.enrollment_id
                WHERE e.student_id = %s AND e.status = '已选'
                ORDER BY s.exam_time DESC
            """, (self.student_id,))
            
            grades = cursor.fetchall()
            
            # 计算统计信息
            total_credit = 0
            total_score = 0
            passed_count = 0
            valid_scores = []

            # 显示成绩信息
            for grade in grades:
                course_name, teacher_name, credit, score, exam_time = grade
                
                # 处理空值
                score = score if score is not None else "未考试"
                exam_time = exam_time.strftime('%Y-%m-%d') if exam_time else "未安排"
                
                self.grade_tree.insert("", "end", values=(
                    course_name,
                    teacher_name or "未分配",
                    credit,
                    score,
                    exam_time
                ))

                # 统计信息计算
                if isinstance(score, (int, float)):
                    total_credit += credit
                    total_score += score * credit
                    if score >= 60:
                        passed_count += 1
                    valid_scores.append(score)

            # 更新统计信息
            if valid_scores:
                avg_score = total_score / total_credit if total_credit > 0 else 0
                pass_rate = (passed_count / len(valid_scores)) * 100 if valid_scores else 0
                
                self.stats_labels["total_credit"].configure(text=f"{total_credit:.1f}")
                self.stats_labels["avg_score"].configure(text=f"{avg_score:.1f}")
                self.stats_labels["pass_rate"].configure(text=f"{pass_rate:.1f}%")
                self.stats_labels["highest_score"].configure(text=f"{max(valid_scores):.1f}")
                self.stats_labels["lowest_score"].configure(text=f"{min(valid_scores):.1f}")
            else:
                for label in self.stats_labels.values():
                    label.configure(text="--")

        except Exception as e:
            messagebox.showerror("错误", f"加载成绩信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
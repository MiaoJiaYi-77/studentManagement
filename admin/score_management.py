import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from styles.form_styles import apply_form_styles

class ScoreManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_scores()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="成绩管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 搜索区域
        search_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        search_frame.pack(fill=tk.X, pady=10)
        
        # 学生搜索
        ctk.CTkLabel(search_frame, text="学生：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT, padx=5)
        self.student_var = tk.StringVar()
        self.student_combo = ctk.CTkOptionMenu(search_frame, variable=self.student_var,
                                             command=self.on_student_selected,
                                             width=150, height=32,
                                             font=ctk.CTkFont(family="微软雅黑", size=12),
                                             fg_color="#4a90e2",
                                             button_color="#357abd",
                                             button_hover_color="#2980b9")
        self.student_combo.pack(side=tk.LEFT, padx=5)
        
        # 课程搜索
        ctk.CTkLabel(search_frame, text="课程：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT, padx=5)
        self.course_var = tk.StringVar()
        self.course_combo = ctk.CTkOptionMenu(search_frame, variable=self.course_var,
                                            command=self.on_course_selected,
                                            width=150, height=32,
                                            font=ctk.CTkFont(family="微软雅黑", size=12),
                                            fg_color="#4a90e2",
                                            button_color="#357abd",
                                            button_hover_color="#2980b9")
        self.course_combo.pack(side=tk.LEFT, padx=5)
        
        # 搜索按钮
        self.search_btn = ctk.CTkButton(search_frame, text="搜索", 
                                      command=self.search_scores,
                                      font=ctk.CTkFont(family="微软雅黑", size=12),
                                      width=100, height=32,
                                      fg_color="#4a90e2",
                                      hover_color="#357abd")
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        self.reset_btn = ctk.CTkButton(search_frame, text="重置", 
                                     command=self.reset_search,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     width=100, height=32,
                                     fg_color="#f0f0f0",
                                     text_color="#333333",
                                     hover_color="#e0e0e0")
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.edit_btn = ctk.CTkButton(btn_frame, text="录入成绩", 
                                    command=self.edit_score,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                       command=self.refresh_scores,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#4a90e2",
                                       hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "student_name", "course_name", "score", "update_time")
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
            "id": "ID", 
            "student_name": "学生姓名",
            "course_name": "课程名称",
            "score": "成绩",
            "update_time": "更新时间"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id"]:
                width = 80
            elif col in ["score"]:
                width = 100
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_score())
        
        # 加载下拉框数据
        self.load_students()
        self.load_courses()

    def load_courses(self):
        """加载课程列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.id, c.name, t.name as teacher_name
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                ORDER BY c.id
            """)
            
            courses = cursor.fetchall()
            self.courses_dict = {str(c[0]): {"name": c[1], "teacher": c[2]} for c in courses}
            self.course_combo.configure(values=["全部课程"] + [f"{cid} | {info['name']}" 
                                         for cid, info in self.courses_dict.items()])
            self.course_var.set("全部课程")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载课程列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_selected_course(self):
        """获取当前选中的课程信息"""
        course_selection = self.course_var.get()
        if course_selection == "全部课程":
            return None, None
            
        try:
            course_id = course_selection.split(" | ")[0]
            course_info = self.courses_dict.get(course_id)
            if course_info:
                return course_id, course_info["name"]
            return None, None
        except:
            return None, None

    def refresh_scores(self):
        """刷新成绩列表"""
        try:
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 构建查询条件
            conditions = []
            params = []
            
            # 课程筛选
            course_selection = self.course_var.get()
            if course_selection and course_selection != "全部课程":
                course_id = course_selection.split(" | ")[0]
                conditions.append("c.id = %s")
                params.append(course_id)
            
            # 学生筛选
            student_selection = self.student_var.get()
            if student_selection and student_selection != "":
                # 从 "学号 - 姓名" 格式中提取学号
                student_id = student_selection.split(" - ")[0]
                conditions.append("s.id = %s")
                params.append(student_id)
            
            # 构建WHERE子句
            where_clause = " AND ".join(conditions)
            if where_clause:
                where_clause = "WHERE " + where_clause
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            query = f"""
                SELECT e.id, s.id, s.name, c.name, sc.score, sc.exam_time, e.status
                FROM enrollments e
                JOIN students s ON e.student_id = s.id
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN scores sc ON e.id = sc.enrollment_id
                {where_clause}
                ORDER BY e.id
            """
            
            cursor.execute(query, params)
            
            # 填充数据
            for row in cursor.fetchall():
                display_row = list(row)
                if row[4] is None:
                    display_row[4] = "未录入"
                if row[5]:
                    display_row[5] = row[5].strftime('%Y-%m-%d')
                else:
                    display_row[5] = "未设置"
                self.tree.insert('', tk.END, values=display_row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            
    def load_scores(self):
        """加载成绩列表（包装方法）"""
        self.refresh_scores()

    def analyze_scores(self):
        """显示成绩分析"""
        try:
            # 获取当前选中的课程
            course_id, course_name = self.get_selected_course()
            if not course_id:
                messagebox.showwarning("提示", "请先选择一个具体的课程！")
                return
            
            # 查询成绩数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sc.score
                FROM enrollments e
                JOIN scores sc ON e.id = sc.enrollment_id
                WHERE e.course_id = %s AND sc.score IS NOT NULL
            """, (course_id,))
            
            scores = [row[0] for row in cursor.fetchall()]
            
            if not scores:
                messagebox.showwarning("提示", "该课程暂无成绩数据！")
                return
            
            # 创建分析窗口
            analysis_window = tk.Toplevel(self.parent_frame)
            analysis_window.title(f"成绩分析 - {course_name}")
            analysis_window.geometry("800x600")
            
            # 设置模态
            analysis_window.grab_set()
            analysis_window.transient(self.parent_frame)
            
            # 居中显示
            analysis_window.update_idletasks()
            x = (analysis_window.winfo_screenwidth() - 800) // 2
            y = (analysis_window.winfo_screenheight() - 600) // 2
            analysis_window.geometry(f"800x600+{x}+{y}")
            
            # 创建统计信息框架
            stats_frame = ttk.Frame(analysis_window, padding="10")
            stats_frame.pack(fill=tk.X)
            
            # 计算统计数据
            avg_score = np.mean(scores)
            max_score = np.max(scores)
            min_score = np.min(scores)
            median_score = np.median(scores)
            std_score = np.std(scores)
            
            # 显示统计信息
            stats_text = f"""
            课程：{course_name}
            总人数：{len(scores)}
            平均分：{avg_score:.2f}
            最高分：{max_score:.2f}
            最低分：{min_score:.2f}
            中位数：{median_score:.2f}
            标准差：{std_score:.2f}
            """
            ttk.Label(stats_frame, text=stats_text, font=("微软雅黑", 11)).pack()
            
            # 创建图表框架
            chart_frame = ttk.Frame(analysis_window)
            chart_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建图表
            fig = plt.Figure(figsize=(8, 4))
            
            # 成绩分布直方图
            ax1 = fig.add_subplot(121)
            ax1.hist(scores, bins=10, edgecolor='black')
            ax1.set_title('成绩分布')
            ax1.set_xlabel('分数')
            ax1.set_ylabel('人数')
            
            # 成绩区间统计
            ax2 = fig.add_subplot(122)
            score_ranges = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
            range_counts = []
            range_labels = ['不及格', '及格', '中等', '良好', '优秀']
            
            for start, end in score_ranges:
                count = sum(1 for s in scores if start <= s < end)
                range_counts.append(count)
            
            ax2.bar(range_labels, range_counts)
            ax2.set_title('成绩等级分布')
            ax2.set_xlabel('等级')
            ax2.set_ylabel('人数')
            
            # 调整布局
            fig.tight_layout()
            
            # 将图表添加到窗口
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("错误", f"分析失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def export_scores(self):
        """导出成绩"""
        try:
            # 获取当前选中的课程
            course_id, course_name = self.get_selected_course()
            where_clause = ""
            params = []
            file_name = "全部课程成绩"
            
            if course_id:
                where_clause = "WHERE c.id = %s"
                params = [course_id]
                file_name = f"{course_name}成绩"
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            query = f"""
                SELECT s.id as 学号, s.name as 姓名,
                       c.name as 课程名称, sc.score as 成绩,
                       sc.exam_time as 考试时间, e.status as 状态
                FROM enrollments e
                JOIN students s ON e.student_id = s.id
                JOIN courses c ON e.course_id = c.id
                LEFT JOIN scores sc ON e.id = sc.enrollment_id
                {where_clause}
                ORDER BY c.id, s.id
            """
            cursor.execute(query, params)
            
            # 获取数据
            rows = cursor.fetchall()
            if not rows:
                messagebox.showwarning("提示", "没有数据可导出！")
                return
            
            # 导出到CSV文件
            import csv
            from tkinter import filedialog
            
            # 获取保存路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{file_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not file_path:
                return
            
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow([d[0] for d in cursor.description])
                # 写入数据
                for row in rows:
                    # 转换日期格式
                    row_list = list(row)
                    if row[4]:  # exam_time
                        row_list[4] = row[4].strftime('%Y-%m-%d')
                    writer.writerow(row_list)
            
            messagebox.showinfo("成功", f"成绩已导出到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def input_score(self):
        """录入成绩"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要录入成绩的记录！")
            return
        
        values = self.tree.item(selected[0], 'values')
        if values[4] != "未录入":
            messagebox.showinfo("提示", "该记录已有成绩，请使用编辑功能！")
            return
        
        self.open_score_form(values, is_edit=False)

    def edit_score(self):
        """编辑成绩"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的记录！")
            return
        
        values = self.tree.item(selected[0], 'values')
        if values[4] == "未录入":
            messagebox.showinfo("提示", "该记录未录入成绩，请使用录入功能！")
            return
            
        self.open_score_form(values, is_edit=True)

    def delete_score(self):
        """删除成绩"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除成绩的记录！")
            return
        
        values = self.tree.item(selected[0], 'values')
        if values[4] == "未录入":
            messagebox.showinfo("提示", "该记录尚未录入成绩！")
            return
        
        if not messagebox.askyesno("确认", "确定要删除这条成绩记录吗？"):
            return
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM scores WHERE enrollment_id = %s", (values[0],))
            conn.commit()
            
            messagebox.showinfo("成功", "成绩已删除！")
            self.refresh_scores()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_score_form(self, values, is_edit=False):
        """打开成绩录入/编辑表单"""
        enrollment_id = values[0]
        student_name = values[2]
        course_name = values[3]
        current_score = values[4] if is_edit else None
        current_date = values[5] if is_edit and values[5] != "未设置" else None
        
        # 创建窗口
        form = ctk.CTkToplevel(self.parent_frame)
        form.title(f"{'编辑' if is_edit else '录入'}成绩")
        
        # 设置模态
        form.grab_set()
        form.transient(self.parent_frame)
        
        # 居中显示
        self.center_window(form, 550, 700)
        
        # 创建表单框架
        form_frame = ctk.CTkFrame(form, fg_color="#f8f9fa")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 存储变量
        self.field_vars = {}
        
        # 显示学生和课程信息
        ctk.CTkLabel(form_frame, text="学生：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=0, pady=10, sticky="e")
        ctk.CTkLabel(form_frame, text=student_name, 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=1, pady=10, sticky="w")
        
        ctk.CTkLabel(form_frame, text="课程：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=1, column=0, pady=10, sticky="e")
        ctk.CTkLabel(form_frame, text=course_name, 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=1, column=1, pady=10, sticky="w")
        
        # 成绩输入
        ctk.CTkLabel(form_frame, text="成绩：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=2, column=0, pady=10, sticky="e")
        score_var = tk.StringVar(value=current_score if current_score != "未录入" else "")
        score_entry = ctk.CTkEntry(form_frame, textvariable=score_var,
                                 width=200, height=32,
                                 font=ctk.CTkFont(family="微软雅黑", size=12))
        score_entry.grid(row=2, column=1, pady=10, sticky="w")
        self.field_vars['score'] = score_var
        
        # 考试时间
        ctk.CTkLabel(form_frame, text="考试时间：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=3, column=0, pady=10, sticky="e")
        date_var = tk.StringVar(value=current_date or datetime.now().strftime('%Y-%m-%d'))
        date_entry = ctk.CTkEntry(form_frame, textvariable=date_var,
                                 width=200, height=32,
                                 font=ctk.CTkFont(family="微软雅黑", size=12))
        date_entry.grid(row=3, column=1, pady=10, sticky="w")
        
        def validate_and_save():
            try:
                # 获取并验证成绩
                score_text = score_var.get().strip()
                if not score_text:
                    messagebox.showerror("错误", "请输入成绩！")
                    score_entry.focus()
                    return False
                
                try:
                    score_float = float(score_text)
                    if not (0 <= score_float <= 100):
                        messagebox.showerror("错误", "成绩必须在0-100之间！")
                        score_entry.focus()
                        return False
                except ValueError:
                    messagebox.showerror("错误", "成绩必须是数字！")
                    score_entry.focus()
                    return False
                
                # 获取并验证日期
                exam_date = date_var.get().strip()
                try:
                    datetime.strptime(exam_date, '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("错误", "日期格式不正确，请使用YYYY-MM-DD格式！")
                    date_entry.focus()
                    return False
                
                # 保存到数据库
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                
                try:
                    if is_edit:
                        cursor.execute("""
                            UPDATE scores 
                            SET score = %s, exam_time = %s
                            WHERE enrollment_id = %s
                        """, (score_float, exam_date, enrollment_id))
                    else:
                        cursor.execute("""
                            INSERT INTO scores (enrollment_id, score, exam_time)
                            VALUES (%s, %s, %s)
                        """, (enrollment_id, score_float, exam_date))
                    
                    conn.commit()
                    messagebox.showinfo("成功", "保存成功！")
                    self.refresh_scores()
                    form.destroy()
                    return True
                    
                except mysql.connector.Error as e:
                    conn.rollback()
                    messagebox.showerror("数据库错误", f"保存失败：{str(e)}")
                    return False
                finally:
                    if 'conn' in locals():
                        conn.close()
                        
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
                return False
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=validate_and_save,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     width=100, height=32,
                     fg_color="#4a90e2",
                     hover_color="#357abd").pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        ctk.CTkButton(btn_frame, text="取消", 
                     command=form.destroy,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color="#f0f0f0",
                     text_color="#333333",
                     hover_color="#e0e0e0",
                     width=100, height=32).pack(side=tk.LEFT, padx=10)
        
        # 防止窗口被关闭时的验证错误
        form.protocol("WM_DELETE_WINDOW", form.destroy)

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

    def on_student_selected(self, choice):
        """学生选择回调"""
        self.search_scores()

    def on_course_selected(self, choice):
        """课程选择回调"""
        self.search_scores()

    def search_scores(self):
        """搜索成绩"""
        self.refresh_scores()

    def reset_search(self):
        """重置搜索条件"""
        self.student_var.set("")
        self.course_var.set("全部课程")
        self.refresh_scores()

    def load_students(self):
        """加载学生列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name
                FROM students
                ORDER BY id
            """)
            
            students = cursor.fetchall()
            if students:
                student_options = [""] + [f"{s[0]} - {s[1]}" for s in students]
                self.student_combo.configure(values=student_options)
                self.student_var.set("")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载学生列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
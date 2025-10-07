import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig

class CourseScheduleManagement:
    def __init__(self, parent_frame, course_id=None, course_name=None):
        self.parent_frame = parent_frame
        self.course_id = course_id
        self.course_name = course_name
        self.setup_ui()
        self.load_schedules()

    def setup_ui(self):
        # 设置样式
        style = ttk.Style()
        style.configure("Custom.TButton", padding=6, relief="flat", background="#007bff")
        
        # 主框架
        self.frame = ttk.Frame(self.parent_frame)
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title = "课程时间安排"
        if self.course_name:
            title += f" - {self.course_name}"
        ttk.Label(title_frame, text=title, font=("黑体", 20)).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ttk.Button(btn_frame, text="新增时间", command=self.add_schedule, style="Custom.TButton")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(btn_frame, text="编辑时间", command=self.edit_schedule, style="Custom.TButton")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="删除时间", command=self.delete_schedule, style="Custom.TButton")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(btn_frame, text="刷新", command=self.refresh_schedules, style="Custom.TButton")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建表格
        columns = ("id", "start_week", "end_week", "weekday", "class_period", "classroom", "remark")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16,
                                yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=self.tree.yview)
        
        # 设置表头
        column_text = {
            "id": "ID", 
            "start_week": "开始周",
            "end_week": "结束周",
            "weekday": "星期",
            "class_period": "节次",
            "classroom": "教室",
            "remark": "备注"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id", "start_week", "end_week", "class_period"]:
                width = 80
            elif col in ["weekday", "classroom"]:
                width = 100
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_schedule())

    def refresh_schedules(self):
        """刷新课程时间列表"""
        try:
            # 禁用刷新按钮，防止重复点击
            self.refresh_btn.config(state='disabled')
            
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            query = """
                SELECT id, start_week, end_week, weekday, class_period, 
                       classroom, remark
                FROM course_schedule
                WHERE course_id = %s
                ORDER BY start_week, FIELD(weekday, '星期一', '星期二', '星期三', 
                                        '星期四', '星期五', '星期六', '星期日'),
                         class_period
            """
            cursor.execute(query, (self.course_id,))
            
            # 填充数据
            for row in cursor.fetchall():
                self.tree.insert('', tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            # 启用刷新按钮
            self.refresh_btn.config(state='normal')
            
    def load_schedules(self):
        """加载课程时间列表（包装方法）"""
        self.refresh_schedules()

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_schedules()
        form.destroy()

    def add_schedule(self):
        self.open_schedule_form()

    def edit_schedule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的时间安排！")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_schedule_form(values)

    def delete_schedule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的时间安排！")
            return
        
        schedule_id = self.tree.item(selected[0], 'values')[0]
        if not messagebox.askyesno("确认", f"确定要删除ID为 {schedule_id} 的时间安排吗？"):
            return
            
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 删除时间安排
            cursor.execute("DELETE FROM course_schedule WHERE id = %s", (schedule_id,))
            conn.commit()
            messagebox.showinfo("成功", "删除成功！")
            self.load_schedules()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_schedule_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = tk.Toplevel(self.parent_frame)
        form.title("编辑时间安排" if is_edit else "新增时间安排")
        form.geometry("500x500")
        form.resizable(False, False)
        
        # 设置模态
        form.grab_set()
        form.transient(self.parent_frame)
        
        # 居中显示
        form.update_idletasks()
        x = (form.winfo_screenwidth() - 500) // 2
        y = (form.winfo_screenheight() - 500) // 2
        form.geometry(f"500x500+{x}+{y}")
        
        # 创建样式
        style = ttk.Style()
        style.configure("Form.TLabel", font=("微软雅黑", 11))
        style.configure("Form.TButton", font=("微软雅黑", 11), padding=5)
        
        # 创建表单框架
        form_frame = ttk.Frame(form, padding="20 15 20 15")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 存储变量
        self.field_vars = {}
        
        # 创建输入字段
        fields = [
            ("开始周：", "start_week", values[1] if is_edit else ""),
            ("结束周：", "end_week", values[2] if is_edit else ""),
            ("星期：", "weekday", values[3] if is_edit else "星期一"),
            ("节次：", "class_period", values[4] if is_edit else ""),
            ("教室：", "classroom", values[5] if is_edit else ""),
            ("备注：", "remark", values[6] if is_edit else "")
        ]
        
        # 创建输入框
        for i, (label_text, field_name, default_value) in enumerate(fields):
            ttk.Label(form_frame, text=label_text, style="Form.TLabel").grid(row=i, column=0, pady=10, sticky="e")
            
            if field_name == "weekday":
                var = tk.StringVar(form, value=default_value)
                combo = ttk.Combobox(form_frame, textvariable=var, 
                                   values=["星期一", "星期二", "星期三", "星期四", 
                                          "星期五", "星期六", "星期日"],
                                   state='readonly', width=30, font=("微软雅黑", 11))
                combo.grid(row=i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
            elif field_name == "remark":
                var = tk.StringVar(form, value=default_value)
                entry = ttk.Entry(form_frame, textvariable=var, width=32, font=("微软雅黑", 11))
                entry.grid(row=i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
            else:
                var = tk.StringVar(form, value=default_value)
                entry = ttk.Entry(form_frame, textvariable=var, width=32, font=("微软雅黑", 11))
                entry.grid(row=i, column=1, pady=10, sticky="w")
                self.field_vars[field_name] = var
        
        # 按钮区域
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def on_submit(event=None):
            try:
                # 获取并验证输入
                data = {field: var.get().strip() for field, var in self.field_vars.items()}
                
                # 验证必填字段
                required_fields = {
                    "start_week": "开始周",
                    "end_week": "结束周",
                    "weekday": "星期",
                    "class_period": "节次",
                    "classroom": "教室"
                }
                for field, name in required_fields.items():
                    if not data[field]:
                        messagebox.showerror("错误", f"{name}不能为空！")
                        return
                
                # 验证数字字段
                try:
                    start_week = int(data['start_week'])
                    end_week = int(data['end_week'])
                    class_period = int(data['class_period'])
                    
                    if start_week <= 0 or end_week <= 0:
                        messagebox.showerror("错误", "周数必须大于0！")
                        return
                    if start_week > end_week:
                        messagebox.showerror("错误", "开始周不能大于结束周！")
                        return
                    if class_period <= 0:
                        messagebox.showerror("错误", "节次必须大于0！")
                        return
                except ValueError:
                    messagebox.showerror("错误", "周数和节次必须是整数！")
                    return
                
                try:
                    conn = mysql.connector.connect(**DatabaseConfig.get_config())
                    cursor = conn.cursor()
                    
                    # 检查时间冲突
                    conflict_check_sql = """
                        SELECT COUNT(*) FROM course_schedule
                        WHERE weekday = %s AND class_period = %s AND
                              ((start_week BETWEEN %s AND %s) OR
                               (end_week BETWEEN %s AND %s) OR
                               (start_week <= %s AND end_week >= %s)) AND
                              classroom = %s
                    """
                    if is_edit:
                        conflict_check_sql += " AND id != %s"
                        cursor.execute(conflict_check_sql, (
                            data['weekday'], data['class_period'],
                            start_week, end_week, start_week, end_week,
                            start_week, end_week, data['classroom'], values[0]
                        ))
                    else:
                        cursor.execute(conflict_check_sql, (
                            data['weekday'], data['class_period'],
                            start_week, end_week, start_week, end_week,
                            start_week, end_week, data['classroom']
                        ))
                    
                    if cursor.fetchone()[0] > 0:
                        messagebox.showerror("错误", "该教室在选择的时间段已被占用！")
                        return
                    
                    if is_edit:
                        # 更新时间安排
                        cursor.execute("""
                            UPDATE course_schedule 
                            SET start_week=%s, end_week=%s, weekday=%s,
                                class_period=%s, classroom=%s, remark=%s 
                            WHERE id=%s
                        """, (
                            start_week, end_week, data['weekday'],
                            class_period, data['classroom'], data['remark'],
                            values[0]
                        ))
                        conn.commit()
                        messagebox.showinfo("成功", "保存成功！")
                        self.load_schedules()
                        form.destroy()
                    else:
                        # 创建时间安排
                        cursor.execute("""
                            INSERT INTO course_schedule 
                            (course_id, start_week, end_week, weekday,
                             class_period, classroom, remark)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            self.course_id, start_week, end_week,
                            data['weekday'], class_period,
                            data['classroom'], data['remark']
                        ))
                        
                        conn.commit()
                        messagebox.showinfo("成功", "添加成功！")
                        self.load_schedules()
                        form.destroy()
                    
                except mysql.connector.Error as e:
                    conn.rollback()
                    messagebox.showerror("数据库错误", f"保存失败：{str(e)}\n错误代码：{e.errno}")
                    return
                except Exception as e:
                    messagebox.showerror("未知错误", f"发生未知错误：{str(e)}")
                    return
                finally:
                    if 'conn' in locals():
                        conn.close()
                        
            except Exception as e:
                messagebox.showerror("错误", f"操作失败：{str(e)}")
        
        # 绑定回车键到提交按钮
        form.bind('<Return>', on_submit)
        
        ttk.Button(btn_frame, text="保存", command=on_submit, style="Form.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=lambda: self.on_form_close(form), style="Form.TButton").pack(side=tk.LEFT, padx=10)
        
        # 防止窗口被关闭时的验证错误
        form.protocol("WM_DELETE_WINDOW", lambda: self.on_form_close(form)) 
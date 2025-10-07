import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class PersonalInfo:
    def __init__(self, parent_frame, student_id):
        self.parent_frame = parent_frame
        self.student_id = student_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_info()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="个人信息", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主信息框架
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 内容区
        content_box = ctk.CTkFrame(main_frame, fg_color="white",
                                  border_width=2, border_color="#4a90e2", corner_radius=10)
        content_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 定义字段
        self.fields = [
            ("姓名", ""),
            ("性别", ""),
            ("出生日期", ""),
            ("班级", ""),
            ("电话", ""),
            ("邮箱", ""),
            ("地址", ""),
            ("入学日期", ""),
            ("状态", "")
        ]

        # 创建输入框字典
        self.entries = {}

        # 创建字段
        for i, (field, _) in enumerate(self.fields):
            frame = ctk.CTkFrame(content_box, fg_color="transparent")
            frame.pack(fill=tk.X, pady=8)
            
            # 标签
            ctk.CTkLabel(frame, text=f"{field}：", width=100, 
                        anchor="e", font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT)
            
            # 输入框或下拉框
            if field == "性别":
                entry = ctk.CTkOptionMenu(frame, values=["男", "女"], 
                                        width=250,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        fg_color="#4a90e2",
                                        button_color="#357abd",
                                        button_hover_color="#2980b9",
                                        state="disabled")
            else:
                entry = ctk.CTkEntry(frame, width=250, height=32,
                                   font=ctk.CTkFont(family="微软雅黑", size=12),
                                   state="disabled")
            entry.pack(side=tk.LEFT, padx=10)
            
            self.entries[field] = entry

        # 按钮框架
        button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        button_frame.pack(pady=15)

        # 编辑按钮
        self.edit_btn = ctk.CTkButton(button_frame, text="编辑信息",
                                     command=self.edit_info,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     width=120,
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=10)

        # 保存按钮
        self.save_btn = ctk.CTkButton(button_frame, text="保存",
                                     command=self.save_info,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     width=120,
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd",
                                     state="disabled")
        self.save_btn.pack(side=tk.LEFT, padx=10)

    def load_info(self):
        """加载个人信息"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 查询学生信息（包括班级信息）
            query = """
                SELECT s.name, s.gender, s.birth, c.name, s.phone, s.email, 
                       s.address, s.enroll_date, s.status
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                WHERE s.id = %s
            """
            cursor.execute(query, (self.student_id,))
            row = cursor.fetchone()
            
            if not row:
                messagebox.showerror("错误", "未找到学生信息！")
                return

            # 定义字段顺序
            fields = ["姓名", "性别", "出生日期", "班级", "电话", "邮箱", "地址", "入学日期", "状态"]
            
            # 更新界面上的值
            for field, value in zip(fields, row):
                if value is None:
                    value = ""
                elif isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d')
                
                entry = self.entries[field]
                if isinstance(entry, ctk.CTkOptionMenu):
                    entry.configure(state="normal")
                    entry.set(str(value))
                    entry.configure(state="disabled")
                else:
                    entry.configure(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
                    entry.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("错误", f"加载信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def edit_info(self):
        """进入编辑模式"""
        editable_fields = ["姓名", "性别", "出生日期", "电话", "邮箱", "地址"]
        for field, entry in self.entries.items():
            if field in editable_fields:
                if isinstance(entry, ctk.CTkOptionMenu):
                    entry.configure(state="normal")
                else:
                    entry.configure(state="normal")
        
        self.save_btn.configure(state="normal")
        self.edit_btn.configure(state="disabled")

    def save_info(self):
        """保存修改的信息"""
        try:
            # 获取输入的值
            data = {
                "姓名": self.entries["姓名"].get().strip(),
                "性别": self.entries["性别"].get().strip(),
                "出生日期": self.entries["出生日期"].get().strip(),
                "电话": self.entries["电话"].get().strip(),
                "邮箱": self.entries["邮箱"].get().strip(),
                "地址": self.entries["地址"].get().strip()
            }

            # 验证必填字段
            if not data["姓名"]:
                messagebox.showerror("错误", "姓名不能为空！")
                return

            # 验证日期格式
            if data["出生日期"]:
                try:
                    datetime.strptime(data["出生日期"], "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("错误", "出生日期格式不正确，请使用YYYY-MM-DD格式！")
                    return

            # 保存到数据库
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE students 
                SET name=%s, gender=%s, birth=%s, phone=%s, email=%s, address=%s
                WHERE id=%s
            """, (
                data["姓名"], data["性别"],
                data["出生日期"] or None,
                data["电话"], data["邮箱"], data["地址"],
                self.student_id
            ))

            conn.commit()
            messagebox.showinfo("成功", "保存成功！")
            
            # 重新加载信息
            self.load_info()
            
            # 恢复只读状态
            for field, entry in self.entries.items():
                if field != "班级" and field != "入学日期" and field != "状态":
                    entry.configure(state="disabled")
            
            self.save_btn.configure(state="disabled")
            self.edit_btn.configure(state="normal")

        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"保存失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
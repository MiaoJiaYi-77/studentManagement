import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class NoticeView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_notices()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="公告通知", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主框架
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建左侧公告列表框架
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # 公告列表标题
        ctk.CTkLabel(list_frame, text="公告列表", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(0, 5))

        # 创建公告列表
        self.notice_list = ttk.Treeview(list_frame, columns=("title", "date"), show="headings", height=20,
                                       style="Form.Treeview")
        self.notice_list.column("title", width=300)
        self.notice_list.column("date", width=150)
        self.notice_list.heading("title", text="标题")
        self.notice_list.heading("date", text="发布时间")
        
        # 添加滚动条
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.notice_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.notice_list.configure(yscrollcommand=scrollbar.set)
        self.notice_list.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 绑定选择事件
        self.notice_list.bind('<<TreeviewSelect>>', self.on_select_notice)

        # 创建右侧内容框架
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 公告内容标题
        ctk.CTkLabel(content_frame, text="公告内容", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(0, 5))

        # 创建内容显示区域
        content_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 添加发布者和发布时间标签
        info_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.publisher_label = ctk.CTkLabel(info_frame, text="发布者：",
                                          font=ctk.CTkFont(family="微软雅黑", size=12))
        self.publisher_label.pack(side=tk.LEFT)
        
        self.date_label = ctk.CTkLabel(info_frame, text="发布时间：",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
        self.date_label.pack(side=tk.RIGHT)

        # 创建内容文本框
        self.content_text = ctk.CTkTextbox(content_container, width=500, height=400,
                                         font=ctk.CTkFont(family="微软雅黑", size=12))
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def load_notices(self):
        """加载公告列表"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.notice_list.get_children():
                self.notice_list.delete(item)

            # 查询公告信息
            cursor.execute("""
                SELECT n.id, n.title, n.create_time
                FROM notices n
                ORDER BY n.create_time DESC
            """)
            
            notices = cursor.fetchall()

            # 显示公告列表
            for notice in notices:
                notice_id, title, create_time = notice
                self.notice_list.insert("", "end", iid=notice_id, values=(
                    title,
                    create_time.strftime('%Y-%m-%d %H:%M')
                ))

        except Exception as e:
            messagebox.showerror("错误", f"加载公告列表失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def on_select_notice(self, event):
        """当选择公告时显示详细内容"""
        selected_items = self.notice_list.selection()
        if not selected_items:
            return

        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 查询公告详细信息
            cursor.execute("""
                SELECT n.title, n.content, n.create_time, 
                       CASE u.role 
                           WHEN '教师' THEN t.name
                           WHEN '管理员' THEN u.username
                           ELSE u.username
                       END as publisher_name
                FROM notices n
                JOIN users u ON n.publisher_id = u.id
                LEFT JOIN teachers t ON n.publisher_id = t.id
                WHERE n.id = %s
            """, (selected_items[0],))
            
            notice = cursor.fetchone()
            if notice:
                title, content, create_time, publisher = notice
                
                # 更新发布者和时间信息
                self.publisher_label.configure(text=f"发布者：{publisher}")
                self.date_label.configure(text=f"发布时间：{create_time.strftime('%Y-%m-%d %H:%M')}")
                
                # 更新内容
                self.content_text.delete("0.0", "end")
                self.content_text.insert("0.0", f"{title}\n\n")
                self.content_text.insert("end", content)

        except Exception as e:
            messagebox.showerror("错误", f"加载公告内容失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
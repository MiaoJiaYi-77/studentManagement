import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class RewardsPunishmentsQuery:
    def __init__(self, parent_frame, student_id):
        self.parent_frame = parent_frame
        self.student_id = student_id
        apply_form_styles()  # 应用统一样式
        self.setup_ui()
        self.load_records()

    def setup_ui(self):
        # 主框架
        self.frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # 标题
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(title_frame, text="奖惩记录", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)

        # 创建主框架
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建过滤框架
        filter_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # 类型筛选
        ctk.CTkLabel(filter_frame, text="类型：",
                    font=ctk.CTkFont(family="微软雅黑", size=12)).pack(side=tk.LEFT, padx=(0, 5))
        self.type_var = tk.StringVar(value="全部")
        self.type_combobox = ctk.CTkOptionMenu(filter_frame, 
                                             variable=self.type_var,
                                             values=["全部", "奖励", "惩罚"],
                                             width=120,
                                             font=ctk.CTkFont(family="微软雅黑", size=12),
                                             fg_color="#4a90e2",
                                             button_color="#357abd",
                                             button_hover_color="#2980b9")
        self.type_combobox.pack(side=tk.LEFT, padx=(0, 20))

        # 查询按钮
        ctk.CTkButton(filter_frame, text="查询",
                     command=self.load_records,
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     width=100,
                     height=32,
                     fg_color="#4a90e2",
                     hover_color="#357abd").pack(side=tk.LEFT)

        # 表格区
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建记录列表
        columns = ("日期", "类型", "原因")
        self.records_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                       style="Form.Treeview")
        
        # 设置列宽和标题
        self.records_tree.column("日期", width=150)
        self.records_tree.column("类型", width=100)
        self.records_tree.column("原因", width=400)
        
        for col in columns:
            self.records_tree.heading(col, text=col)

        # 创建滚动条
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.records_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动条
        self.records_tree.configure(yscrollcommand=scrollbar.set)
        self.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建统计信息框架
        stats_frame = ctk.CTkFrame(self.frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 统计标题
        ctk.CTkLabel(stats_frame, text="统计信息", 
                    font=ctk.CTkFont(family="微软雅黑", size=14, weight="bold")).pack(pady=(5, 10))

        # 统计信息标签
        self.stats_labels = {}
        stats_items = [
            ("total", "总记录数："),
            ("rewards", "奖励次数："),
            ("punishments", "惩罚次数：")
        ]

        # 创建统计信息网格
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=5)
        
        for i, (key, text) in enumerate(stats_items):
            # 标签
            ctk.CTkLabel(stats_grid, text=text,
                        font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=i*2, padx=15, pady=10, sticky="e")
            # 值
            value_label = ctk.CTkLabel(stats_grid, text="--",
                                     font=ctk.CTkFont(family="微软雅黑", size=12))
            value_label.grid(row=0, column=i*2+1, padx=15, pady=10, sticky="w")
            self.stats_labels[key] = value_label

    def load_records(self):
        """加载奖惩记录"""
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()

            # 清空现有数据
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)

            # 构建查询条件
            conditions = ["student_id = %s"]
            params = [self.student_id]

            if self.type_var.get() != "全部":
                conditions.append("type = %s")
                params.append(self.type_var.get())

            # 查询奖惩记录
            query = f"""
                SELECT date, type, reason
                FROM rewards_punishments
                WHERE {' AND '.join(conditions)}
                ORDER BY date DESC
            """
            
            cursor.execute(query, tuple(params))
            records = cursor.fetchall()

            # 显示记录信息
            for record in records:
                date, type_, reason = record
                self.records_tree.insert("", "end", values=(
                    date.strftime('%Y-%m-%d'),
                    type_,
                    reason
                ))

            # 计算统计信息
            stats = {
                'total': len(records),
                'rewards': sum(1 for r in records if r[1] == '奖励'),
                'punishments': sum(1 for r in records if r[1] == '惩罚')
            }

            # 更新统计信息
            if stats['total'] > 0:
                self.stats_labels["total"].configure(text=str(stats['total']))
                self.stats_labels["rewards"].configure(text=str(stats['rewards']))
                self.stats_labels["punishments"].configure(text=str(stats['punishments']))
            else:
                for label in self.stats_labels.values():
                    label.configure(text="--")

        except Exception as e:
            messagebox.showerror("错误", f"加载奖惩记录失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close() 
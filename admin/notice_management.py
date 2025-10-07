import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import DatabaseConfig
from datetime import datetime
from styles.form_styles import apply_form_styles

class NoticeManagement:
    def __init__(self, parent_frame, user_id):
        self.parent_frame = parent_frame
        self.current_user_id = user_id  # 存储当前用户ID
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
        ctk.CTkLabel(title_frame, text="通知管理", 
                    font=ctk.CTkFont(family="微软雅黑", size=24, weight="bold")).pack(side=tk.LEFT)
        
        # 按钮区
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 创建按钮并存储引用
        self.add_btn = ctk.CTkButton(btn_frame, text="发布通知", 
                                    command=self.add_notice,
                                    font=ctk.CTkFont(family="微软雅黑", size=12),
                                    height=32,
                                    fg_color="#4a90e2",
                                    hover_color="#357abd")
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="编辑通知", 
                                     command=self.edit_notice,
                                     font=ctk.CTkFont(family="微软雅黑", size=12),
                                     height=32,
                                     fg_color="#4a90e2",
                                     hover_color="#357abd")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="删除通知", 
                                       command=self.delete_notice,
                                       font=ctk.CTkFont(family="微软雅黑", size=12),
                                       height=32,
                                       fg_color="#e74c3c",
                                       hover_color="#c0392b")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", 
                                        command=self.refresh_notices,
                                        font=ctk.CTkFont(family="微软雅黑", size=12),
                                        height=32,
                                        fg_color="#4a90e2",
                                        hover_color="#357abd")
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # 表格区
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("id", "title", "content", "publish_time", "publisher")
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
            "id": "通知ID", 
            "title": "标题",
            "content": "内容",
            "publish_time": "发布时间",
            "publisher": "发布者"
        }
        for col in columns:
            self.tree.heading(col, text=column_text[col])
            # 根据内容类型设置列宽
            if col in ["id"]:
                width = 80
            elif col in ["title", "publisher"]:
                width = 150
            elif col in ["content"]:
                width = 300
            else:
                width = 150
            self.tree.column(col, anchor=tk.CENTER, width=width, minwidth=width)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_notice())

    def refresh_notices(self):
        """刷新公告列表"""
        try:
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 查询数据
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            query = """
                SELECT n.id, n.title, n.content, n.create_time, u.username
                FROM notices n
                JOIN users u ON n.publisher_id = u.id
                ORDER BY n.create_time DESC
            """
            cursor.execute(query)
            
            # 填充数据
            for row in cursor.fetchall():
                display_row = list(row)
                display_row[3] = row[3].strftime('%Y-%m-%d %H:%M')
                self.tree.insert('', tk.END, values=display_row)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
            
    def load_notices(self):
        """加载公告列表（包装方法）"""
        self.refresh_notices()

    def add_notice(self):
        """发布新公告"""
        self.open_notice_form()

    def edit_notice(self):
        """编辑公告"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的公告！")
            return
        
        notice_id = self.tree.item(selected[0], 'values')[0]
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 检查是否是发布者
            cursor.execute("""
                SELECT title, content, publisher_id 
                FROM notices 
                WHERE id = %s
            """, (notice_id,))
            
            notice = cursor.fetchone()
            if not notice:
                messagebox.showerror("错误", "公告不存在！")
                return
            
            self.open_notice_form((notice_id, notice[0], notice[1]))
            
        except Exception as e:
            messagebox.showerror("错误", f"获取公告信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_notice(self):
        """删除公告"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的公告！")
            return
        
        notice_id = self.tree.item(selected[0], 'values')[0]
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            # 检查是否是发布者
            cursor.execute("SELECT publisher_id FROM notices WHERE id = %s", (notice_id,))
            publisher_id = cursor.fetchone()
            
            if not publisher_id:
                messagebox.showerror("错误", "公告不存在！")
                return
                
            if publisher_id[0] != self.current_user_id:
                messagebox.showerror("错误", "只能删除自己发布的公告！")
                return
            
            if not messagebox.askyesno("确认", "确定要删除这条公告吗？"):
                return
            
            cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
            conn.commit()
            
            messagebox.showinfo("成功", "公告已删除！")
            self.refresh_notices()
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("错误", f"删除失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def view_notice(self):
        """查看公告详情"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要查看的公告！")
            return
        
        notice_id = self.tree.item(selected[0], 'values')[0]
        
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT n.title, n.content, u.username, n.create_time
                FROM notices n
                JOIN users u ON n.publisher_id = u.id
                WHERE n.id = %s
            """, (notice_id,))
            
            notice = cursor.fetchone()
            if not notice:
                messagebox.showerror("错误", "公告不存在！")
                return
            
            # 创建查看窗口
            view_window = tk.Toplevel(self.parent_frame)
            view_window.title(f"查看公告 - {notice[0]}")
            view_window.geometry("600x400")
            
            # 设置模态
            view_window.grab_set()
            view_window.transient(self.parent_frame)
            
            # 居中显示
            view_window.update_idletasks()
            x = (view_window.winfo_screenwidth() - 600) // 2
            y = (view_window.winfo_screenheight() - 400) // 2
            view_window.geometry(f"600x400+{x}+{y}")
            
            # 创建内容框架
            content_frame = ttk.Frame(view_window, padding="20 15 20 15")
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # 显示标题
            ttk.Label(content_frame, text=notice[0], 
                     font=("微软雅黑", 14, "bold")).pack(pady=(0, 10))
            
            # 显示发布信息
            info_text = f"发布者：{notice[2]}    发布时间：{notice[3].strftime('%Y-%m-%d %H:%M')}"
            ttk.Label(content_frame, text=info_text, 
                     font=("微软雅黑", 10)).pack(pady=(0, 20))
            
            # 显示内容
            content_text = tk.Text(content_frame, wrap=tk.WORD, 
                                 font=("微软雅黑", 11), height=12)
            content_text.pack(fill=tk.BOTH, expand=True)
            content_text.insert('1.0', notice[1])
            content_text.config(state='disabled')
            
            # 关闭按钮
            ttk.Button(content_frame, text="关闭", 
                      command=view_window.destroy, 
                      style="Custom.TButton").pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取公告信息失败：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def open_notice_form(self, values=None):
        is_edit = values is not None
        
        # 创建弹窗
        form = ctk.CTkToplevel(self.parent_frame)
        form.title("编辑通知" if is_edit else "发布通知")
        
        # 设置模态
        form.grab_set()
        form.transient(self.parent_frame)
        
        # 居中显示 - 调整窗口大小为更合适的尺寸
        self.center_window(form, 500, 450)  # 修改窗口尺寸为 500x450
        
        # 创建表单框架
        form_frame = ctk.CTkFrame(form, fg_color="#f8f9fa")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 新增：内容区外框
        content_box = ctk.CTkFrame(
            form_frame,
            fg_color="white",
            border_width=2,
            border_color="#4a90e2",
            corner_radius=10
        )
        content_box.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # 存储变量
        self.field_vars = {}

        # 标题输入
        ctk.CTkLabel(content_box, text="标题：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=0, column=0, pady=5, sticky="e")
        title_var = tk.StringVar(value=values[1] if is_edit else "")
        title_entry = ctk.CTkEntry(content_box, textvariable=title_var,
                                 width=400, height=32,
                                 font=ctk.CTkFont(family="微软雅黑", size=12))
        title_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.field_vars['title_entry'] = title_entry
        
        # 内容输入
        ctk.CTkLabel(content_box, text="内容：", 
                    font=ctk.CTkFont(family="微软雅黑", size=12)).grid(row=1, column=0, pady=5, sticky="ne")
        content_text = ctk.CTkTextbox(content_box, width=400, height=200,  # 将内容框高度改为200
                                    font=ctk.CTkFont(family="微软雅黑", size=12))
        content_text.grid(row=1, column=1, pady=5, sticky="w")
        if is_edit:
            content_text.insert("1.0", values[2])
        self.field_vars['content'] = content_text
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 保存按钮
        ctk.CTkButton(btn_frame, text="保存", 
                     command=lambda: self.save_notice(form, values[0] if is_edit else None),
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     width=100, height=32,
                     fg_color="#4a90e2",
                     hover_color="#357abd").pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        ctk.CTkButton(btn_frame, text="取消", 
                     command=lambda: self.on_form_close(form),
                     font=ctk.CTkFont(family="微软雅黑", size=12),
                     fg_color="#f0f0f0",
                     text_color="#333333",
                     hover_color="#e0e0e0",
                     width=100, height=32).pack(side=tk.LEFT, padx=10)
        
        # 防止窗口被关闭时的验证错误
        form.protocol("WM_DELETE_WINDOW", lambda: self.on_form_close(form))

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

    def on_form_close(self, form):
        """表单关闭时的回调函数"""
        self.refresh_notices()
        form.destroy()

    def save_notice(self, form, notice_id=None):
        """保存通知信息"""
        try:
            # 获取并验证输入
            title = self.field_vars['title_entry'].get().strip()
            content = self.field_vars['content'].get("0.0", "end").strip()
            
            # 验证必填字段
            if not title:
                messagebox.showerror("错误", "标题不能为空！")
                return
            
            if not content:
                messagebox.showerror("错误", "内容不能为空！")
                return
            
            try:
                conn = mysql.connector.connect(**DatabaseConfig.get_config())
                cursor = conn.cursor()
                
                if notice_id:  # 编辑模式
                    # 更新通知
                    cursor.execute("""
                        UPDATE notices 
                        SET title=%s, content=%s 
                        WHERE id=%s
                    """, (title, content, notice_id))
                else:  # 新增模式
                    # 创建通知
                    cursor.execute("""
                        INSERT INTO notices (title, content, create_time, publisher_id)
                        VALUES (%s, %s, NOW(), %s)
                    """, (title, content, self.current_user_id))
                
                conn.commit()
                messagebox.showinfo("成功", "保存成功！")
                self.refresh_notices()
                form.destroy()
                
            except mysql.connector.Error as e:
                conn.rollback()
                messagebox.showerror("数据库错误", f"保存失败：{str(e)}")
                return
            finally:
                if 'conn' in locals():
                    conn.close()
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}") 
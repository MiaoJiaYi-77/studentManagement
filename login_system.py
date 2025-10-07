import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import hashlib
from db_config import DatabaseConfig
from main_window import MainWindow
import ctypes


class LoginSystem:
    def __init__(self):
        # 启用 DPI 感知
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

        self.root = tk.Tk()
        # 在创建任何窗口部件之前设置缩放因子
        self.root.tk.call('tk', 'scaling', self.root.tk.call('tk', 'scaling'))

        self.root.title("学生管理系统 - 登录")
        self.root.geometry("400x320")
        self.root.configure(bg="#e9ecef")
        self.root.resizable(False, False)

        # 居中窗口
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 320) // 2
        self.root.geometry(f"400x320+{x}+{y}")

        # 样式配置
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", font=("微软雅黑", 11))
        style.configure("TButton", font=("微软雅黑", 11), padding=6)
        style.configure("Header.TLabel", font=("黑体", 16, "bold"), foreground="#343a40", background="#ffffff")
        style.configure("TEntry", padding=4, relief="flat")
        # 按钮主色和次色
        style.configure("Primary.TButton", background="#1976d2", foreground="#fff", borderwidth=0)
        style.map("Primary.TButton",
                  background=[('active', '#1565c0'), ('pressed', '#0d47a1')],
                  foreground=[('disabled', '#ccc')])
        style.configure("Secondary.TButton", background="#bdbdbd", foreground="#222", borderwidth=0)
        style.map("Secondary.TButton",
                  background=[('active', '#9e9e9e'), ('pressed', '#757575')],
                  foreground=[('disabled', '#eee')])

        # 始终创建 login_frame
        self.login_frame = ttk.Frame(self.root, padding="24 18 24 18", style="TFrame")
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.create_login_widgets()
        self.root.bind('<Return>', lambda e: self.login() if hasattr(self,
                                                                     'username_entry') and self.username_entry.focus_get() else None)
        self.main_frame = None

    def clear_card(self):
        for widget in self.login_frame.winfo_children():
            widget.destroy()

    def create_login_widgets(self):
        self.clear_card()
        # 用户登录标题紧贴顶部
        ttk.Label(self.login_frame, text="用户登录", style="Header.TLabel").grid(row=0, column=0, columnspan=2,
                                                                                 pady=(0, 8))
        ttk.Label(self.login_frame, text="用户名：").grid(row=1, column=0, sticky=tk.E, padx=5, pady=8)
        self.username_entry = ttk.Entry(self.login_frame, width=22, font=("微软雅黑", 11))
        self.username_entry.grid(row=1, column=1, pady=8)
        self.username_entry.focus()
        ttk.Label(self.login_frame, text="密码：").grid(row=2, column=0, sticky=tk.E, padx=5, pady=8)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=22, font=("微软雅黑", 11))
        self.password_entry.grid(row=2, column=1, pady=8)
        # 按钮同一行，居中且有空隙
        btn_frame = ttk.Frame(self.login_frame, style="TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=16)
        login_btn = ttk.Button(btn_frame, text="登 录", command=self.login, style="Primary.TButton")
        reg_btn = ttk.Button(btn_frame, text="注册新用户", command=self.create_register_widgets,
                             style="Primary.TButton")
        login_btn.pack(side=tk.LEFT, ipadx=10, padx=(0, 18))
        reg_btn.pack(side=tk.LEFT, ipadx=10)

    def create_register_widgets(self):
        self.clear_card()
        # 用户注册标题紧贴顶部
        ttk.Label(self.login_frame, text="用户注册", style="Header.TLabel").grid(row=0, column=0, columnspan=2,
                                                                                 pady=(0, 8))
        ttk.Label(self.login_frame, text="用户名：").grid(row=1, column=0, sticky=tk.E, padx=5, pady=6)
        self.reg_username_entry = ttk.Entry(self.login_frame, width=22, font=("微软雅黑", 11))
        self.reg_username_entry.grid(row=1, column=1, pady=6)
        self.reg_username_entry.focus()
        ttk.Label(self.login_frame, text="密码：").grid(row=2, column=0, sticky=tk.E, padx=5, pady=6)
        self.reg_password_entry = ttk.Entry(self.login_frame, show="*", width=22, font=("微软雅黑", 11))
        self.reg_password_entry.grid(row=2, column=1, pady=6)
        ttk.Label(self.login_frame, text="确认密码：").grid(row=3, column=0, sticky=tk.E, padx=5, pady=6)
        self.reg_confirm_entry = ttk.Entry(self.login_frame, show="*", width=22, font=("微软雅黑", 11))
        self.reg_confirm_entry.grid(row=3, column=1, pady=6)
        ttk.Label(self.login_frame, text="用户类型：").grid(row=4, column=0, sticky=tk.E, padx=5, pady=6)
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(self.login_frame, textvariable=self.role_var, values=['学生', '教师', '管理员'],
                                  state='readonly', width=20, font=("微软雅黑", 11))
        role_combo.grid(row=4, column=1, pady=6)
        role_combo.set('学生')
        # 按钮同一行，居中且有空隙
        btn_frame = ttk.Frame(self.login_frame, style="TFrame")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=14)
        reg_btn = ttk.Button(btn_frame, text="注 册", command=self.register, style="Primary.TButton")
        back_btn = ttk.Button(btn_frame, text="返回登录", command=self.create_login_widgets, style="Primary.TButton")
        reg_btn.pack(side=tk.LEFT, ipadx=10, padx=(0, 18))
        back_btn.pack(side=tk.LEFT, ipadx=10)

    # 哈希加密
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码！")
            return
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute("SELECT id, role FROM users WHERE username = %s AND password = %s",
                           (username, hashed_password))
            user = cursor.fetchone()
            if user:
                user_id, role = user
                if role == '学生':
                    cursor.execute("SELECT id FROM students WHERE id = %s", (user_id,))
                    if not cursor.fetchone():
                        messagebox.showerror("错误", "未找到对应的学生信息！")
                        return
                # 隐藏登录窗口，显示主界面
                self.root.withdraw()
                if self.main_frame:
                    self.main_frame.root.destroy()
                self.main_frame = MainWindow(user_id, role, self.root)
                self.main_frame.root.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
            else:
                messagebox.showerror("错误", "用户名或密码错误！")
        except Error as e:
            messagebox.showerror("错误", f"数据库错误：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def on_main_window_close(self):
        if self.main_frame:
            self.main_frame.root.destroy()
            self.main_frame = None
        # 重新显示登录窗口
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def register(self):
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        role = self.role_var.get()
        if not username or not password or not confirm:
            messagebox.showerror("错误", "所有字段都必须填写！")
            return
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致！")
            return
        if len(password) < 6:
            messagebox.showerror("错误", "密码长度至少为6位！")
            return
        try:
            conn = mysql.connector.connect(**DatabaseConfig.get_config())
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("错误", "该用户名已被注册！")
                return
            hashed_password = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
            conn.commit()
            messagebox.showinfo("成功", "注册成功！")
            self.create_login_widgets()
        except Error as e:
            messagebox.showerror("错误", f"数据库错误：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LoginSystem()
    app.run()

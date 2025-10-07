import tkinter as tk
from tkinter import ttk
from student.personal_info import PersonalInfo

def main():
    root = tk.Tk()
    root.title("个人信息测试")
    
    # 设置窗口大小和位置
    window_width = 600
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 创建主框架
    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    # 使用ID为5的学生（张小明）
    personal_info = PersonalInfo(main_frame, student_id=5)
    
    root.mainloop()

if __name__ == "__main__":
    main() 
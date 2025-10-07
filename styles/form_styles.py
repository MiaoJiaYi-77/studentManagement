import tkinter as tk
from tkinter import ttk

def apply_form_styles():
    """应用表单样式"""
    style = ttk.Style()
    
    # 表单标签样式
    style.configure(
        "Form.TLabel",
        font=("微软雅黑", 11),
        padding=(5, 5),
        background="#f0f0f0"
    )
    
    # 表单输入框样式
    style.configure(
        "Form.TEntry",
        font=("微软雅黑", 11),
        padding=(5, 5),
        fieldbackground="white",
        borderwidth=1
    )
    
    # 表单下拉框样式
    style.configure(
        "Form.TCombobox",
        font=("微软雅黑", 11),
        padding=(5, 5),
        fieldbackground="white",
        borderwidth=1
    )
    
    # 表单按钮样式
    style.configure(
        "Form.TButton",
        font=("微软雅黑", 11),
        padding=(20, 10),
        background="#4a90e2",
        foreground="white"
    )
    
    # 表单按钮悬停样式
    style.map(
        "Form.TButton",
        background=[("active", "#357abd")],
        foreground=[("active", "white")]
    )
    
    # 删除按钮样式
    style.configure(
        "Delete.TButton",
        font=("微软雅黑", 11),
        padding=(20, 10),
        background="#e74c3c",
        foreground="white"
    )
    
    # 删除按钮悬停样式
    style.map(
        "Delete.TButton",
        background=[("active", "#c0392b")],
        foreground=[("active", "white")]
    )
    
    # 表单框架样式
    style.configure(
        "Form.TFrame",
        background="#f8f9fa",
        relief="flat",
        borderwidth=0
    )
    
    # 表格样式
    style.configure(
        "Form.Treeview",
        font=("微软雅黑", 10),
        rowheight=30,
        background="white",
        fieldbackground="white",
        foreground="black",
        borderwidth=1
    )
    
    # 表格标题样式
    style.configure(
        "Form.Treeview.Heading",
        font=("微软雅黑", 10, "bold"),
        background="#e9ecef",
        foreground="black",
        relief="flat"
    )
    
    # 表格选中行样式
    style.map(
        "Form.Treeview",
        background=[("selected", "#4a90e2")],
        foreground=[("selected", "white")]
    ) 
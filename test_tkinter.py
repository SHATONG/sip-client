import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Tkinter测试")
    root.geometry("300x200")
    
    label = ttk.Label(root, text="测试窗口")
    label.pack(pady=0)
    
    button = ttk.Button(root, text="确定", command=root.destroy)
    button.pack(pady=10)
    
    root.mainloop()
    print("程序正常结束")

if __name__ == "__main__":
    main() 
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import keyboard

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电脑连点器")
        self.root.geometry("400x450")
        self.root.resizable(False, False)

        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))

        # 防止pyautogui的安全特性
        pyautogui.FAILSAFE = False

        # 连点状态
        self.running = False
        self.click_thread = None

        # 点击模式变量
        self.click_mode = tk.StringVar(value="limited")

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 连点类型选择
        ttk.Label(main_frame, text="连点类型:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.click_type = tk.StringVar(value="鼠标左键")
        click_types = ["鼠标左键", "鼠标右键", "鼠标中键"] + [chr(i) for i in range(65, 91)]  # A-Z
        ttk.Combobox(main_frame, textvariable=self.click_type, values=click_types, width=15).grid(row=0, column=1, sticky=tk.W, pady=5)

        # 连点间隔设置
        ttk.Label(main_frame, text="连点间隔(秒):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.interval = tk.DoubleVar(value=0.1)
        ttk.Scale(main_frame, variable=self.interval, from_=0.01, to=1.0, orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, sticky=tk.W, pady=5)
        # 创建一个标签来显示实际间隔时间
        self.interval_label = ttk.Label(main_frame, text=f"{self.interval.get():.2f}")
        self.interval_label.grid(row=1, column=2, sticky=tk.W, padx=5)
        self.interval.trace_add("write", lambda *args: self.update_interval_label())

        # 连点次数设置
        ttk.Label(main_frame, text="连点次数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.click_count = tk.IntVar(value=10)
        self.click_count_entry = ttk.Entry(main_frame, textvariable=self.click_count, width=10)
        self.click_count_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="有限次", variable=self.click_mode, value="limited").grid(row=2, column=2, sticky=tk.W, padx=5)
        ttk.Radiobutton(main_frame, text="无限次", variable=self.click_mode, value="unlimited").grid(row=2, column=3, sticky=tk.W, padx=5)

        # 快捷键设置
        ttk.Label(main_frame, text="开始/暂停快捷键:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.hotkey = tk.StringVar(value="F6")
        ttk.Combobox(main_frame, textvariable=self.hotkey, values=["F5", "F6", "F7", "F8", "F9"], width=5).grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="停止快捷键:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.stop_hotkey = tk.StringVar(value="F10")
        ttk.Combobox(main_frame, textvariable=self.stop_hotkey, values=["F8", "F9", "F10", "F11", "F12"], width=5).grid(row=4, column=1, sticky=tk.W, pady=5)

        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, text="当前状态:", font=("SimHei", 12, "bold")).grid(row=5, column=0, sticky=tk.W, pady=20)
        ttk.Label(main_frame, textvariable=self.status_var, font=("SimHei", 12, "bold"), foreground="red").grid(row=5, column=1, sticky=tk.W, pady=20)

        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=20)

        self.start_button = ttk.Button(button_frame, text="开始", command=self.toggle_clicking, width=12)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_clicking, width=12, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # 帮助信息
        ttk.Label(main_frame, text="提示: 运行时鼠标指针会自动点击").grid(row=7, column=0, columnspan=4, sticky=tk.W, pady=5)

        # 绑定快捷键
        keyboard.add_hotkey(self.hotkey.get(), self.toggle_clicking)
        keyboard.add_hotkey(self.stop_hotkey.get(), self.stop_clicking)

    def update_interval_label(self):
        """更新间隔显示标签"""
        self.interval_label.config(text=f"{self.interval.get():.2f}")

    def toggle_clicking(self):
        """开始或暂停连点"""
        if self.running:
            self.running = False
            self.start_button.config(text="开始")
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("已暂停")
        else:
            try:
                # 验证连点次数输入
                count = self.click_count.get()
                if self.click_mode.get() == "limited" and count <= 0:
                    messagebox.showerror("输入错误", "有限次连点的次数必须大于0。")
                    return
                self.running = True
                self.start_button.config(text="暂停")
                self.stop_button.config(state=tk.NORMAL)
                self.status_var.set("运行中...")

                if not self.click_thread or not self.click_thread.is_alive():
                    self.click_thread = threading.Thread(target=self.perform_clicks)
                    self.click_thread.daemon = True
                    self.click_thread.start()
            except ValueError:
                messagebox.showerror("输入错误", "连点次数必须是整数。")

    def stop_clicking(self):
        """完全停止连点并重置状态"""
        self.running = False
        self.start_button.config(text="开始")
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("已停止")

    def perform_clicks(self):
        """执行连点操作的线程函数"""
        click_type = self.click_type.get()
        interval = self.interval.get()
        count = self.click_count.get()

        # 给用户准备时间
        for i in range(3, 0, -1):
            if not self.running:
                return
            self.status_var.set(f"准备中: {i}")
            time.sleep(1)

        self.status_var.set("运行中...")

        if self.click_mode.get() == "limited":
            # 有限次连点
            for i in range(count):
                if not self.running:
                    break

                try:
                    self.perform_action(click_type)
                    self.status_var.set(f"运行中: {i+1}/{count}")
                    time.sleep(interval)
                except Exception as e:
                    messagebox.showerror("操作错误", f"执行操作时出现错误: {str(e)}")
                    self.stop_clicking()
                    return
        else:
            # 无限次连点
            counter = 0
            while self.running:
                try:
                    self.perform_action(click_type)
                    counter += 1
                    self.status_var.set(f"运行中: {counter}")
                    time.sleep(interval)
                except Exception as e:
                    messagebox.showerror("操作错误", f"执行操作时出现错误: {str(e)}")
                    self.stop_clicking()
                    return

        # 连点完成
        if self.running:
            self.running = False
            self.start_button.config(text="开始")
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("连点完成")

    def perform_action(self, action):
        """执行具体的点击或按键操作"""
        if action == "鼠标左键":
            pyautogui.click(button='left')
        elif action == "鼠标右键":
            pyautogui.click(button='right')
        elif action == "鼠标中键":
            pyautogui.click(button='middle')
        else:
            # 键盘按键
            pyautogui.press(action.lower())

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
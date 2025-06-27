import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import keyboard
from pynput import keyboard as pynput_keyboard


class KeySelectorDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("选择按键")
        self.geometry("600x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_key = None

        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 创建UI
        ttk.Label(self, text="请点击或按下想要添加的按键:").pack(pady=20)

        # 按键列表
        self.key_frame = ttk.Frame(self)
        self.key_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # 常用特殊按键
        special_keys = [
            "鼠标左键", "鼠标右键", "鼠标中键",
            "ctrl", "shift", "alt",
            "left", "right", "up", "down",
            "kp_0", "kp_1", "kp_2", "kp_3", "kp_4",
            "kp_5", "kp_6", "kp_7", "kp_8", "kp_9",
            "kp_dot", "kp_plus", "kp_minus", "kp_multiply", "kp_divide"
        ]

        # 创建按键按钮
        for i, key in enumerate(special_keys):
            col = i % 5
            row = i // 5
            ttk.Button(self.key_frame, text=key, command=lambda k=key: self.select_key(k)).grid(
                row=row, column=col, padx=5, pady=5, sticky="nsew"
            )

        # 监听键盘事件
        self.listener = pynput_keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        # 关闭时停止监听
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_key_press(self, key):
        try:
            # 处理字符键
            if hasattr(key, 'char'):
                self.selected_key = key.char
                self.destroy()
            # 处理特殊键
            elif hasattr(key, 'name'):
                key_map = {
                    'left': 'left',
                    'right': 'right',
                    'up': 'up',
                    'down': 'down',
                    'ctrl': 'ctrl',
                    'shift': 'shift',
                    'alt': 'alt',
                    'page_up': 'pageup',
                    'page_down': 'pagedown',
                    'home': 'home',
                    'end': 'end',
                    'insert': 'insert',
                    'delete': 'delete',
                    'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
                    'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
                    'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
                    # 小键盘键
                    'kp_0': 'kp0',
                    'kp_1': 'kp1',
                    'kp_2': 'kp2',
                    'kp_3': 'kp3',
                    'kp_4': 'kp4',
                    'kp_5': 'kp5',
                    'kp_6': 'kp6',
                    'kp_7': 'kp7',
                    'kp_8': 'kp8',
                    'kp_9': 'kp9',
                    'decimal': 'kp_dot',
                    'add': 'kp_plus',
                    'subtract': 'kp_minus',
                    'multiply': 'kp_multiply',
                    'divide': 'kp_divide',
                }
                if key.name in key_map:
                    self.selected_key = key_map[key.name]
                    self.destroy()
        except Exception as e:
            print(f"Error handling key press: {e}")

    def select_key(self, key):
        self.selected_key = key
        self.destroy()

    def on_close(self):
        self.listener.stop()
        self.destroy()


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电脑连点器")
        self.root.geometry("650x500")
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

        # 连点模式变量
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
        click_types = ["鼠标左键", "鼠标右键", "鼠标中键"] + [chr(i) for i in range(65, 91)] + [
            "left", "right", "up", "down", "ctrl", "shift", "alt",
            "kp_0", "kp_1", "kp_2", "kp_3", "kp_4",
            "kp_5", "kp_6", "kp_7", "kp_8", "kp_9",
            "kp_dot", "kp_plus", "kp_minus", "kp_multiply", "kp_divide"
        ]
        ttk.Combobox(main_frame, textvariable=self.click_type, values=click_types, width=15).grid(
            row=0, column=1, sticky=tk.W, pady=5)

        # 多个键位输入
        ttk.Label(main_frame, text="多个键位:").grid(row=0, column=2, sticky=tk.W, pady=5)

        # 创建一个包含输入框和按钮的框架
        key_input_frame = ttk.Frame(main_frame)
        key_input_frame.grid(row=0, column=3, sticky=tk.W, pady=5)

        # 使用tk.Text作为多行输入框
        self.multi_keys_text = tk.Text(key_input_frame, height=3, width=20)
        self.multi_keys_text.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(key_input_frame, text="选择按键", command=self.select_keys).pack(side=tk.LEFT)

        # 连点间隔设置
        ttk.Label(main_frame, text="连点间隔(秒):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.interval = tk.DoubleVar(value=0.1)
        ttk.Scale(main_frame, variable=self.interval, from_=0.01, to=1.0, orient=tk.HORIZONTAL, length=200).grid(
            row=1, column=1, sticky=tk.W, pady=5)
        self.interval_label = ttk.Label(main_frame, text=f"{self.interval.get():.2f}")
        self.interval_label.grid(row=1, column=2, sticky=tk.W, padx=5)
        self.interval.trace_add("write", lambda *args: self.update_interval_label())

        # 连点次数设置
        ttk.Label(main_frame, text="连点次数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.click_count = tk.IntVar(value=10)
        ttk.Entry(main_frame, textvariable=self.click_count, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="有限次", variable=self.click_mode, value="limited").grid(
            row=2, column=2, sticky=tk.W, padx=5)
        ttk.Radiobutton(main_frame, text="无限次", variable=self.click_mode, value="unlimited").grid(
            row=2, column=3, sticky=tk.W, padx=5)

        # 自定义等待时间设置
        ttk.Label(main_frame, text="自定义等待时间(秒):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.wait_time = tk.DoubleVar(value=0)
        ttk.Entry(main_frame, textvariable=self.wait_time, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)

        # 快捷键设置
        ttk.Label(main_frame, text="开始/暂停快捷键:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.hotkey = tk.StringVar(value="F6")
        ttk.Combobox(main_frame, textvariable=self.hotkey, values=["F5", "F6", "F7", "F8", "F9"], width=5).grid(
            row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="停止快捷键:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.stop_hotkey = tk.StringVar(value="F10")
        ttk.Combobox(main_frame, textvariable=self.stop_hotkey, values=["F8", "F9", "F10", "F11", "F12"], width=5).grid(
            row=5, column=1, sticky=tk.W, pady=5)

        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, text="当前状态:", font=("SimHei", 12, "bold")).grid(row=6, column=0, sticky=tk.W, pady=20)
        ttk.Label(main_frame, textvariable=self.status_var, font=("SimHei", 12, "bold"), foreground="red").grid(
            row=6, column=1, sticky=tk.W, pady=20)

        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=20)

        self.start_button = ttk.Button(button_frame, text="开始", command=self.toggle_clicking, width=12)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_clicking, width=12,
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # 帮助信息
        ttk.Label(main_frame, text="提示: 运行时鼠标指针会自动点击").grid(row=8, column=0, columnspan=4, sticky=tk.W, pady=5)

        # 绑定快捷键
        keyboard.add_hotkey(self.hotkey.get(), self.toggle_clicking)
        keyboard.add_hotkey(self.stop_hotkey.get(), self.stop_clicking)

    def update_interval_label(self):
        """更新间隔显示标签"""
        self.interval_label.config(text=f"{self.interval.get():.2f}")

    def select_keys(self):
        """打开按键选择对话框"""
        dialog = KeySelectorDialog(self.root)
        self.root.wait_window(dialog)

        if dialog.selected_key:
            current_keys = self.multi_keys_text.get("1.0", tk.END).strip()
            if current_keys:
                self.multi_keys_text.insert(tk.END, f",{dialog.selected_key}")
            else:
                self.multi_keys_text.insert(tk.END, dialog.selected_key)

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
        multi_keys_text = self.multi_keys_text.get("1.0", tk.END).strip()
        multi_keys = multi_keys_text.split(',') if multi_keys_text else []
        wait_time = self.wait_time.get()

        # 验证多个键位输入
        valid_keys = [chr(i) for i in range(65, 91)] + ["鼠标左键", "鼠标右键", "鼠标中键", "left", "right", "up",
                                                        "down", "ctrl", "shift", "alt",
                                                        "kp_0", "kp_1", "kp_2", "kp_3", "kp_4",
                                                        "kp_5", "kp_6", "kp_7", "kp_8", "kp_9",
                                                        "kp_dot", "kp_plus", "kp_minus", "kp_multiply", "kp_divide"]
        for key in multi_keys:
            key = key.strip()
            if key and key not in valid_keys:
                messagebox.showerror("输入错误", f"无效的键位: {key}")
                self.running = False
                self.stop_clicking()
                return

        # 自定义等待时间
        if wait_time > 0:
            for i in range(int(wait_time), 0, -1):
                if not self.running:
                    return
                self.status_var.set(f"等待中: {i}")
                time.sleep(1)

        self.status_var.set("运行中...")

        if self.click_mode.get() == "limited":
            # 有限次连点
            for i in range(count):
                if not self.running:
                    break

                if multi_keys:
                    for key in multi_keys:
                        key = key.strip()
                        if key:
                            self.perform_action(key)
                            time.sleep(interval)
                else:
                    self.perform_action(click_type)
                    time.sleep(interval)

                self.status_var.set(f"运行中: {i + 1}/{count}")
        else:
            # 无限次连点
            counter = 0
            while self.running:
                if multi_keys:
                    for key in multi_keys:
                        key = key.strip()
                        if key:
                            self.perform_action(key)
                            time.sleep(interval)
                else:
                    self.perform_action(click_type)
                    time.sleep(interval)

                counter += 1
                self.status_var.set(f"运行中: {counter}")

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
        elif action in ["left", "right", "up", "down", "ctrl", "shift", "alt"]:
            # 使用keyboard库处理标准按键
            keyboard.press_and_release(action)
        elif action.startswith("kp_"):
            # 使用keyboard库处理小键盘按键
            # 将kp_格式转换为keyboard库支持的格式
            keyboard_key = action.replace("kp_", "num_")
            keyboard.press_and_release(keyboard_key)
        else:
            # 键盘按键
            keyboard.press_and_release(action.lower())


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
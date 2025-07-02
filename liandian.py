import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
import keyboard
import sys
import os


class KeySelectorDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("选择按键")
        self.geometry("650x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_key = None
        self.combined_keys = []
        self.is_combining = False
        self.press_hook = None  # 按键按下钩子
        self.release_hook = None  # 按键释放钩子

        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # 创建UI
        ttk.Label(self, text="请点击或按下想要添加的按键:").pack(pady=10)

        # 组合键提示
        self.combo_frame = ttk.Frame(self)
        self.combo_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(self.combo_frame, text="当前组合键:").pack(side=tk.LEFT)
        self.combo_label = ttk.Label(self.combo_frame, text="无", foreground="red")
        self.combo_label.pack(side=tk.LEFT, padx=5)

        self.combine_button = ttk.Button(self.combo_frame, text="开始组合", command=self.toggle_combining)
        self.combine_button.pack(side=tk.RIGHT)

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
        self.press_hook = keyboard.on_press(self.on_key_press)
        self.release_hook = keyboard.on_release(self.on_key_release)

        # 关闭时停止监听
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_combining(self):
        """切换组合键模式"""
        self.is_combining = not self.is_combining
        if self.is_combining:
            self.combine_button.config(text="完成组合")
            self.combined_keys = []
            self.update_combo_label()
        else:
            self.combine_button.config(text="开始组合")
            if self.combined_keys:
                self.selected_key = "+".join(self.combined_keys)
                self.destroy()

    def update_combo_label(self):
        """更新组合键标签"""
        if self.combined_keys:
            self.combo_label.config(text="+".join(self.combined_keys))
        else:
            self.combo_label.config(text="无")

    def on_key_press(self, event):
        """处理键盘按下事件"""
        try:
            key = event.name
            
            # 转换特殊键名
            key_map = {
                'decimal': 'kp_dot',
                'add': 'kp_plus',
                'subtract': 'kp_minus',
                'multiply': 'kp_multiply',
                'divide': 'kp_divide',
                'space': ' ',
                'enter': 'return',
                'backspace': 'back',
                'tab': 'tab',
                'escape': 'esc',
                'delete': 'del',
                'insert': 'ins',
                'home': 'home',
                'end': 'end',
                'page_up': 'pageup',
                'page_down': 'pagedown',
            }
            
            key = key_map.get(key, key)
            
            # 处理字母键
            if len(key) == 1 and key.isalpha():
                key = key.upper()
                
            # 处理数字小键盘
            if key.startswith('numpad'):
                key = 'kp_' + key[6:]
                
            if self.is_combining:
                if key not in self.combined_keys:
                    self.combined_keys.append(key)
                    self.update_combo_label()
            else:
                self.selected_key = key
                self.destroy()
        except Exception as e:
            print(f"Error handling key press: {e}")

    def on_key_release(self, event):
        """处理键盘释放事件"""
        # 可根据需要添加释放事件处理逻辑
        pass

    def select_key(self, key):
        """处理按钮点击选择的键"""
        if self.is_combining:
            if key not in self.combined_keys:
                self.combined_keys.append(key)
                self.update_combo_label()
        else:
            self.selected_key = key
            self.destroy()

    def on_close(self):
        """关闭对话框时清理资源"""
        if self.press_hook:
            keyboard.unhook(self.press_hook)
        if self.release_hook:
            keyboard.unhook(self.release_hook)
        self.destroy()


def resource_path(relative_path):
    """获取打包后/开发时的正确资源路径"""
    if getattr(sys, 'frozen', False):
        # 打包后，资源在 sys._MEIPASS 临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发时，返回相对路径
    return os.path.join(os.path.abspath("."), relative_path)


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电脑连点器")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        # 修复图标加载问题
        self.load_icon()

        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCombobox", font=("SimHei", 10))

        # 连点状态
        self.run_flag = False    # 是否「正在运行」（总开关）
        self.pause_flag = False  # 是否「暂停中」（不影响总计数，仅暂停连点）
        self.current_count = 0   # 当前已完成次数
        self.target_count = 0    # 目标次数（有限循环时用，-1 代表无限）
        self.click_thread = None
        self.stop_event = threading.Event()

        # 连点模式变量
        self.click_mode = tk.StringVar(value="limited")

        # 创建界面
        self.create_widgets()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_icon(self):
        icon_path = resource_path('1.ico')
        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"图标加载失败（非关键错误）: {e}")

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

        # 使用tk.Text作为多行输入框，并添加滚动条
        scroll_frame = ttk.Frame(key_input_frame)
        scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.multi_keys_text = tk.Text(scroll_frame, height=3, width=20, yscrollcommand=scrollbar.set)
        self.multi_keys_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.multi_keys_text.yview)

        ttk.Button(key_input_frame, text="选择按键", command=self.select_keys).pack(side=tk.LEFT, padx=5)

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
        ttk.Label(main_frame, text="开始快捷键:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.hotkey = tk.StringVar(value="F6")
        self.hotkey_entry = ttk.Entry(main_frame, textvariable=self.hotkey, width=5)
        self.hotkey_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="暂停快捷键:").grid(row=4, column=2, sticky=tk.W, pady=5)
        self.pause_hotkey = tk.StringVar(value="F7")
        self.pause_hotkey_entry = ttk.Entry(main_frame, textvariable=self.pause_hotkey, width=5)
        self.pause_hotkey_entry.grid(row=4, column=3, sticky=tk.W, pady=5)

        ttk.Label(main_frame, text="停止快捷键:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.stop_hotkey = tk.StringVar(value="F10")
        self.stop_hotkey_entry = ttk.Entry(main_frame, textvariable=self.stop_hotkey, width=5)
        self.stop_hotkey_entry.grid(row=5, column=1, sticky=tk.W, pady=5)

        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, text="当前状态:", font=("SimHei", 12, "bold")).grid(row=6, column=0, sticky=tk.W, pady=20)
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("SimHei", 12, "bold"), foreground="red")
        self.status_label.grid(row=6, column=1, sticky=tk.W, pady=20)

        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=20)

        self.start_button = ttk.Button(button_frame, text="开始", command=self.start_clicking, width=12)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.pause_button = ttk.Button(button_frame, text="暂停", command=self.pause_clicking, width=12, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        self.resume_button = ttk.Button(button_frame, text="恢复", command=self.resume_clicking, width=12, state=tk.DISABLED)
        self.resume_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_clicking, width=12, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # 帮助信息
        ttk.Label(main_frame, text="提示: 运行时鼠标指针会自动点击").grid(row=8, column=0, columnspan=4, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="组合键使用方法: 使用'开始组合'按钮录制组合键，如 ctrl+alt+a").grid(row=9, column=0, columnspan=4, sticky=tk.W, pady=2)

        # 绑定快捷键
        self.bind_hotkeys()

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
                # 确保新键位添加到新行
                self.multi_keys_text.insert(tk.END, f"\n{dialog.selected_key}")
            else:
                self.multi_keys_text.insert(tk.END, dialog.selected_key)

            # 确保文本框可见
            self.multi_keys_text.see(tk.END)

    def start_clicking(self):
        """开始连点"""
        if self.run_flag:
            return  # 已经在运行中，不重复启动

        try:
            # 验证连点次数输入
            count = self.click_count.get()
            if self.click_mode.get() == "limited" and count <= 0:
                messagebox.showerror("输入错误", "有限次连点的次数必须大于0。")
                return

            # 重置状态
            self.run_flag = True
            self.pause_flag = False  # 确保开始时不是暂停状态
            self.target_count = count if self.click_mode.get() == "limited" else -1
            self.current_count = 0  # 重置当前计数

            # 重置停止事件
            self.stop_event.clear()

            # 确保前一个线程已停止
            if self.click_thread and self.click_thread.is_alive():
                self.click_thread.join(timeout=0.5)

            # 更新UI
            self.status_var.set("准备中...")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # 创建新线程
            self.click_thread = threading.Thread(target=self._click_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
        except ValueError:
            messagebox.showerror("输入错误", "连点次数必须是整数。")
        except Exception as e:
            messagebox.showerror("启动错误", f"无法启动连点线程: {e}")

    def pause_clicking(self):
        """暂停连点"""
        if not self.run_flag or self.pause_flag:
            return  # 未运行或已暂停，无需操作

        self.pause_flag = True
        self.status_var.set("已暂停")
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)

    def resume_clicking(self):
        """恢复连点"""
        if not self.run_flag or not self.pause_flag:
            return  # 未运行或未暂停，无需操作

        self.pause_flag = False
        self.status_var.set(f"恢复运行: {self.current_count}/{self.target_count}" if self.target_count > 0 else f"恢复运行: {self.current_count}")
        self.pause_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

    def stop_clicking(self):
        """强制停止连点"""
        if not self.run_flag:
            return  # 未运行，无需操作

        self.run_flag = False
        self.pause_flag = False
        self.stop_event.set()
        
        self.root.after(0, lambda: self.status_var.set("已强制停止"))
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.current_count = 0  # 重置计数器

        # 确保线程有机会停止
        if self.click_thread and self.click_thread.is_alive():
            try:
                # 等待最多0.5秒让线程完成当前操作
                self.click_thread.join(timeout=0.5)
            except Exception as e:
                print(f"停止线程时出错: {e}")

    def _click_loop(self):
        """连点核心逻辑"""
        multi_keys_text = self.multi_keys_text.get("1.0", tk.END).strip()
        multi_keys = [k.strip() for k in multi_keys_text.splitlines() if k.strip()] if multi_keys_text else []
        wait_time = self.wait_time.get()

        if not self.validate_multi_keys(multi_keys):
            self.run_flag = False
            self.root.after(0, self._update_ui_after_complete)
            return

        # 处理等待时间
        self.handle_wait_time(wait_time)

        # 在进入主循环前检查状态
        if not self.run_flag:
            return

        try:
            # 计算总点击次数
            total_clicks = len(multi_keys) if multi_keys else 1
            
            # 外层循环：控制总次数（有限 or 无限）
            while self.run_flag and (self.target_count < 0 or self.current_count < self.target_count):
                if self.pause_flag:
                    # 暂停时，短暂休眠后重试（避免 CPU 空转）
                    time.sleep(0.1)
                    continue  # 跳过当前连点，等待恢复
                
                # 内层循环：执行一次完整的点击序列
                if multi_keys:
                    for key in multi_keys:
                        if self.stop_event.is_set() or not self.run_flag:
                            return
                        
                        # 执行点击操作
                        self.perform_action(key)
                        
                        # 更新计数
                        self.current_count += 1
                        self.root.after(0, self._update_count_display)
                        
                        # 检查是否达到目标次数
                        if self.target_count > 0 and self.current_count >= self.target_count:
                            break
                        
                        # 检查暂停状态
                        if self.pause_flag:
                            break  # 跳出内层循环，回到外层检查暂停状态
                else:
                    # 执行单个点击操作
                    self.perform_action(self.click_type.get())
                    
                    # 更新计数
                    self.current_count += 1
                    self.root.after(0, self._update_count_display)
                
                # 检查是否达到目标次数
                if self.target_count > 0 and self.current_count >= self.target_count:
                    break
                
                # 检查暂停状态
                if self.pause_flag:
                    continue
                
                # 连点间隔（分解为小片段，支持更及时的暂停响应）
                interval = self.interval.get()
                for _ in range(int(interval * 10)):
                    if self.pause_flag or self.stop_event.is_set() or not self.run_flag:
                        break
                    time.sleep(0.1)

        finally:
            if self.run_flag:
                self.run_flag = False
                self.root.after(0, self._update_ui_after_complete)

    def _update_count_display(self):
        """更新计数显示"""
        if self.target_count > 0:
            self.status_var.set(f"运行中: {self.current_count}/{self.target_count}")
        else:
            self.status_var.set(f"运行中: {self.current_count}")

    def _update_ui_after_complete(self):
        """在连点完成后更新UI"""
        if self.target_count > 0 and self.current_count >= self.target_count:
            self.status_var.set(f"已完成: {self.current_count}/{self.target_count}")
        else:
            self.status_var.set("已停止")
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

    def validate_multi_keys(self, multi_keys):
        valid_keys = [chr(i) for i in range(65, 91)] + ["鼠标左键", "鼠标右键", "鼠标中键", "left", "right", "up",
                                                        "down", "ctrl", "shift", "alt",
                                                        "kp_0", "kp_1", "kp_2", "kp_3", "kp_4",
                                                        "kp_5", "kp_6", "kp_7", "kp_8", "kp_9",
                                                        "kp_dot", "kp_plus", "kp_minus", "kp_multiply", "kp_divide"]
        for key in multi_keys:
            key = key.strip()
            if key:
                if '+' in key:
                    sub_keys = key.split('+')
                    for sub_key in sub_keys:
                        if sub_key not in valid_keys:
                            self.root.after(0, lambda: messagebox.showerror("输入错误", f"无效的组合键成分: {sub_key}"))
                            return False
                elif key not in valid_keys:
                    self.root.after(0, lambda: messagebox.showerror("输入错误", f"无效的键位: {key}"))
                    return False
        return True

    def handle_wait_time(self, wait_time):
        if wait_time > 0:
            for i in range(int(wait_time), 0, -1):
                if self.stop_event.is_set() or not self.run_flag:
                    return
                self.root.after(0, lambda i=i: self.status_var.set(f"准备中: {i}"))

                # 将等待分解为小片段，以便及时响应停止
                for _ in range(10):
                    if self.stop_event.is_set() or not self.run_flag:
                        return
                    time.sleep(0.1)

            self.root.after(0, lambda: self.status_var.set("运行中..."))

    def perform_action(self, action):
        """执行具体的点击或按键操作"""
        if '+' in action:
            # 处理组合键
            keys = action.split('+')

            # 按下所有键
            for key in keys:
                if key == "鼠标左键":
                    pyautogui.mouseDown(button='left')
                elif key == "鼠标右键":
                    pyautogui.mouseDown(button='right')
                elif key == "鼠标中键":
                    pyautogui.mouseDown(button='middle')
                else:
                    # 处理键盘按键
                    keyboard_key = key.replace("kp_", "num_")
                    keyboard.press(keyboard_key)

            # 短暂延迟确保所有键都已按下
            time.sleep(0.05)

            # 释放所有键
            for key in reversed(keys):
                if key == "鼠标左键":
                    pyautogui.mouseUp(button='left')
                elif key == "鼠标右键":
                    pyautogui.mouseUp(button='right')
                elif key == "鼠标中键":
                    pyautogui.mouseUp(button='middle')
                else:
                    # 处理键盘按键
                    keyboard_key = key.replace("kp_", "num_")
                    keyboard.release(keyboard_key)
        else:
            # 处理单个键
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
                keyboard_key = action.replace("kp_", "num_")
                keyboard.press_and_release(keyboard_key)
            else:
                # 键盘按键
                keyboard.press_and_release(action.lower())

    def bind_hotkeys(self):
        """绑定快捷键"""
        try:
            # 尝试移除所有热键
            try:
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass

            # 绑定开始快捷键
            keyboard.add_hotkey(self.hotkey.get(), self.start_clicking)

            # 绑定暂停快捷键
            keyboard.add_hotkey(self.pause_hotkey.get(), self.pause_clicking)

            # 绑定停止快捷键
            keyboard.add_hotkey(self.stop_hotkey.get(), self.stop_clicking)
        except Exception as e:
            print(f"绑定快捷键时出错: {e}")
            messagebox.showerror("快捷键错误", f"无法绑定快捷键: {e}")

    def on_close(self):
        """程序关闭时的清理工作"""
        self.run_flag = False
        self.pause_flag = False
        self.stop_event.set()

        # 安全地等待线程结束
        if self.click_thread and self.click_thread.is_alive():
            try:
                # 等待最多1秒让线程结束
                self.click_thread.join(timeout=1.0)
            except Exception as e:
                print(f"关闭时停止线程出错: {e}")

        # 移除热键
        try:
            keyboard.unhook_all_hotkeys()
        except Exception as e:
            print(f"移除热键时出错: {e}")

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
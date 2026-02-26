import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("番茄钟")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 全局变量
        self.timer_interval = None
        self.remaining_time = 1500  # 默认工作时间（25分钟）
        self.current_mode = 'work'
        self.is_running = False
        self.tasks = []
        self.settings = {
            'work_time': 1500,
            'short_break': 300,
            'long_break': 900,
            'reminder': 'none'
        }
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        
        # 数据文件路径
        self.data_file = 'pomodoro_data.json'
        
        # 颜色定义
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb',
            'success': '#4CAF50',
            'background': '#f5f5f5',
            'card_bg': '#ffffff',
            'text': '#333333',
            'text_light': '#999999'
        }
        
        # 加载数据
        self.load_data()
        
        # 创建主布局
        self.create_main_layout()
        
        # 初始化界面
        self.update_timer_display()
        self.render_tasks()
        self.render_calendar()
    
    def create_main_layout(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右布局
        left_frame = ttk.Frame(main_frame, width=400, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(main_frame, width=600, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 计时器部分
        self.create_timer_section(left_frame)
        
        # 任务管理部分
        self.create_tasks_section(left_frame)
        
        # 日历部分
        self.create_calendar_section(right_frame)
    
    def create_timer_section(self, parent):
        # 创建计时器框架
        timer_frame = ttk.Frame(parent, padding="20", style='Card.TFrame')
        timer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(timer_frame, text="计时器", font=('Helvetica', 16, 'bold'), style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 模式按钮
        mode_frame = ttk.Frame(timer_frame)
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.work_btn = ttk.Button(mode_frame, text="工作", command=lambda: self.set_mode('work'), style='Mode.TButton')
        self.work_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.short_break_btn = ttk.Button(mode_frame, text="短休息", command=lambda: self.set_mode('short-break'), style='Mode.TButton')
        self.short_break_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.long_break_btn = ttk.Button(mode_frame, text="长休息", command=lambda: self.set_mode('long-break'), style='Mode.TButton')
        self.long_break_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # 时间显示
        time_display_frame = ttk.Frame(timer_frame, style='TimeDisplay.TFrame')
        time_display_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        self.time_display = ttk.Label(time_display_frame, text="25:00", style='Time.TLabel')
        self.time_display.pack(expand=True)
        
        # 控制按钮
        control_frame = ttk.Frame(timer_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="开始", command=self.start_timer, style='Control.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.pause_btn = ttk.Button(control_frame, text="暂停", command=self.pause_timer, state=tk.DISABLED, style='Control.TButton')
        self.pause_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.reset_btn = ttk.Button(control_frame, text="重置", command=self.reset_timer, style='Control.TButton')
        self.reset_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # 设置按钮
        settings_frame = ttk.Frame(timer_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        self.settings_btn = ttk.Button(settings_frame, text="⚙️ 设置", command=self.open_settings, style='Settings.TButton')
        self.settings_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_tasks_section(self, parent):
        # 创建任务管理框架
        tasks_frame = ttk.Frame(parent, padding="20", style='Card.TFrame')
        tasks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(tasks_frame, text="任务管理", font=('Helvetica', 16, 'bold'), style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 任务输入
        task_input_frame = ttk.Frame(tasks_frame, style='Input.TFrame')
        task_input_frame.pack(fill=tk.X, pady=10)
        
        self.task_input = ttk.Entry(task_input_frame, style='TaskInput.TEntry')
        self.task_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.add_task_btn = ttk.Button(task_input_frame, text="添加", command=self.add_task, style='AddTask.TButton')
        self.add_task_btn.pack(side=tk.LEFT, padx=5)
        
        # 任务列表
        self.task_list_frame = ttk.Frame(tasks_frame, style='List.TFrame')
        self.task_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.task_list_frame, style='Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 任务列表树
        self.task_tree = ttk.Treeview(self.task_list_frame, columns=('name', 'completed'), show='headings', yscrollcommand=scrollbar.set, style='TaskTree.Treeview')
        self.task_tree.heading('name', text='任务名称')
        self.task_tree.heading('completed', text='完成状态')
        self.task_tree.column('name', width=200)
        self.task_tree.column('completed', width=100, anchor=tk.CENTER)
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.task_tree.yview)
        
        # 任务操作按钮
        task_buttons_frame = ttk.Frame(tasks_frame)
        task_buttons_frame.pack(fill=tk.X, pady=10)
        
        self.edit_task_btn = ttk.Button(task_buttons_frame, text="编辑", command=self.edit_task, state=tk.DISABLED, style='Action.TButton')
        self.edit_task_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.delete_task_btn = ttk.Button(task_buttons_frame, text="删除", command=self.delete_task, state=tk.DISABLED, style='Delete.TButton')
        self.delete_task_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # 绑定任务列表选择事件
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
    
    def create_calendar_section(self, parent):
        # 创建日历框架
        calendar_frame = ttk.Frame(parent, padding="20", style='Card.TFrame')
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(calendar_frame, text="日历视图", font=('Helvetica', 16, 'bold'), style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 日历标题和导航
        calendar_header = ttk.Frame(calendar_frame, style='CalendarHeader.TFrame')
        calendar_header.pack(fill=tk.X, pady=10)
        
        self.prev_month_btn = ttk.Button(calendar_header, text="← 上月", command=self.prev_month, style='Nav.TButton')
        self.prev_month_btn.pack(side=tk.LEFT, padx=5)
        
        self.calendar_title = ttk.Label(calendar_header, text="2026年2月", font=('Helvetica', 16, 'bold'), style='CalendarTitle.TLabel')
        self.calendar_title.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.next_month_btn = ttk.Button(calendar_header, text="下月 →", command=self.next_month, style='Nav.TButton')
        self.next_month_btn.pack(side=tk.RIGHT, padx=5)
        
        # 日历网格
        self.calendar_grid = ttk.Frame(calendar_frame, style='CalendarGrid.TFrame')
        self.calendar_grid.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def open_settings(self):
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("450x350")
        settings_window.transient(self.root)
        settings_window.grab_set()
        settings_window.configure(bg=self.colors['background'])
        
        # 创建设置窗口内容
        settings_frame = ttk.Frame(settings_window, padding="30", style='Card.TFrame')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(settings_frame, text="设置", font=('Helvetica', 18, 'bold'), style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 工作时间设置
        work_time_frame = ttk.Frame(settings_frame, style='Setting.TFrame')
        work_time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(work_time_frame, text="工作时间（分钟）:", font=('Helvetica', 11), style='Label.TLabel').pack(side=tk.LEFT, padx=5, pady=5)
        work_time_var = tk.IntVar(value=self.settings['work_time'] // 60)
        work_time_entry = ttk.Entry(work_time_frame, textvariable=work_time_var, style='SettingEntry.TEntry')
        work_time_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        # 短休息设置
        short_break_frame = ttk.Frame(settings_frame, style='Setting.TFrame')
        short_break_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(short_break_frame, text="短休息（分钟）:", font=('Helvetica', 11), style='Label.TLabel').pack(side=tk.LEFT, padx=5, pady=5)
        short_break_var = tk.IntVar(value=self.settings['short_break'] // 60)
        short_break_entry = ttk.Entry(short_break_frame, textvariable=short_break_var, style='SettingEntry.TEntry')
        short_break_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        # 长休息设置
        long_break_frame = ttk.Frame(settings_frame, style='Setting.TFrame')
        long_break_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(long_break_frame, text="长休息（分钟）:", font=('Helvetica', 11), style='Label.TLabel').pack(side=tk.LEFT, padx=5, pady=5)
        long_break_var = tk.IntVar(value=self.settings['long_break'] // 60)
        long_break_entry = ttk.Entry(long_break_frame, textvariable=long_break_var, style='SettingEntry.TEntry')
        long_break_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        # 提醒设置
        reminder_frame = ttk.Frame(settings_frame, style='Setting.TFrame')
        reminder_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(reminder_frame, text="提醒方式:", font=('Helvetica', 11), style='Label.TLabel').pack(side=tk.LEFT, padx=5, pady=5)
        reminder_var = tk.StringVar(value=self.settings['reminder'])
        reminder_combobox = ttk.Combobox(reminder_frame, textvariable=reminder_var, values=['none', 'notification', 'sound', 'both'], style='SettingCombobox.TCombobox')
        reminder_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        # 保存按钮
        def save_settings():
            self.settings['work_time'] = work_time_var.get() * 60
            self.settings['short_break'] = short_break_var.get() * 60
            self.settings['long_break'] = long_break_var.get() * 60
            self.settings['reminder'] = reminder_var.get()
            
            # 如果当前是工作模式，更新剩余时间
            if self.current_mode == 'work':
                self.remaining_time = self.settings['work_time']
                self.update_timer_display()
            
            self.save_data()
            settings_window.destroy()
            messagebox.showinfo("提示", "设置已保存！")
        
        save_btn = ttk.Button(settings_frame, text="保存", command=save_settings, style='Save.TButton')
        save_btn.pack(pady=30)

    
    def start_timer(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        
        def update_timer():
            self.remaining_time -= 1
            self.update_timer_display()
            
            if self.remaining_time <= 0:
                self.pause_timer()
                self.show_reminder()
                self.switch_mode()
                return
            
            self.timer_interval = self.root.after(1000, update_timer)
        
        update_timer()
    
    def pause_timer(self):
        if not self.is_running:
            return
        
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        
        if self.timer_interval:
            self.root.after_cancel(self.timer_interval)
            self.timer_interval = None
    
    def reset_timer(self):
        self.pause_timer()
        self.set_mode(self.current_mode)
    
    def set_mode(self, mode):
        self.current_mode = mode
        
        # 更新按钮状态
        self.work_btn.config(style='TButton' if mode != 'work' else 'Accent.TButton')
        self.short_break_btn.config(style='TButton' if mode != 'short-break' else 'Accent.TButton')
        self.long_break_btn.config(style='TButton' if mode != 'long-break' else 'Accent.TButton')
        
        # 设置对应时间
        if mode == 'work':
            self.remaining_time = self.settings['work_time']
        elif mode == 'short-break':
            self.remaining_time = self.settings['short_break']
        elif mode == 'long-break':
            self.remaining_time = self.settings['long_break']
        
        self.update_timer_display()
    
    def switch_mode(self):
        if self.current_mode == 'work':
            self.set_mode('short-break')
        else:
            self.set_mode('work')
    
    def update_timer_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_display.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def show_reminder(self):
        if self.settings['reminder'] == 'none':
            return
        
        if self.settings['reminder'] in ['notification', 'both']:
            messagebox.showinfo("番茄钟提醒", f"{'工作时间结束！' if self.current_mode == 'work' else '休息时间结束！'}")
    
    def add_task(self):
        task_name = self.task_input.get().strip()
        if not task_name:
            return
        
        # 如果没有选择日期，使用当天的日期
        date_to_use = self.selected_date or datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.tasks.append({
            'name': f"{date_to_use} - {task_name}",
            'completed': False,
            'date': date_to_use
        })
        
        self.task_input.delete(0, tk.END)
        self.render_tasks()
        self.render_calendar()
        self.save_data()
    
    def on_task_select(self, event):
        selected_items = self.task_tree.selection()
        if selected_items:
            self.edit_task_btn.config(state=tk.NORMAL)
            self.delete_task_btn.config(state=tk.NORMAL)
        else:
            self.edit_task_btn.config(state=tk.DISABLED)
            self.delete_task_btn.config(state=tk.DISABLED)
    
    def edit_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        task_id = int(item)
        task = self.tasks[task_id]
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑任务")
        edit_window.geometry("400x200")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        edit_frame = ttk.Frame(edit_window, padding="20")
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 任务名称输入
        ttk.Label(edit_frame, text="任务名称:").pack(pady=10)
        task_name_var = tk.StringVar(value=task['name'].split(' - ', 1)[1])
        task_name_entry = ttk.Entry(edit_frame, textvariable=task_name_var)
        task_name_entry.pack(fill=tk.X, pady=5)
        
        # 保存按钮
        def save_edit():
            new_name = task_name_var.get().strip()
            if new_name:
                task['name'] = f"{task['date']} - {new_name}"
                self.render_tasks()
                self.render_calendar()
                self.save_data()
                edit_window.destroy()
        
        save_btn = ttk.Button(edit_frame, text="保存", command=save_edit)
        save_btn.pack(pady=20)
    
    def delete_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        task_id = int(item)
        
        if messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
            self.tasks.pop(task_id)
            self.render_tasks()
            self.render_calendar()
            self.save_data()
    
    def render_tasks(self):
        # 清空任务列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 过滤当前选中日期的任务
        filtered_tasks = [task for task in self.tasks if task['date'] == self.selected_date] if self.selected_date else self.tasks
        
        if not filtered_tasks:
            # 显示空任务提示
            pass
        else:
            for i, task in enumerate(filtered_tasks):
                task_name = task['name'].split(' - ', 1)[1] if ' - ' in task['name'] else task['name']
                completed = "是" if task['completed'] else "否"
                self.task_tree.insert('', tk.END, iid=str(i), values=(task_name, completed))
    
    def render_calendar(self):
        # 清空日历网格
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        
        year = self.current_date.year
        month = self.current_date.month
        
        # 更新日历标题
        self.calendar_title.config(text=f"{year}年{month}月")
        
        # 添加星期标题
        weekdays = ['日', '一', '二', '三', '四', '五', '六']
        for i, day in enumerate(weekdays):
            day_label = ttk.Label(self.calendar_grid, text=day, font=('Helvetica', 10, 'bold'))
            day_label.grid(row=0, column=i, sticky=tk.NSEW, padx=2, pady=2)
        
        # 计算日历数据
        first_day = datetime.datetime(year, month, 1)
        start_date = first_day - datetime.timedelta(days=first_day.weekday())
        
        # 添加日期
        for i in range(42):  # 6周 x 7天
            current_date = start_date + datetime.timedelta(days=i)
            row = i // 7 + 1
            col = i % 7
            
            # 创建日期按钮
            date_btn = ttk.Button(
                self.calendar_grid, 
                text=str(current_date.day),
                command=lambda d=current_date: self.select_date(d)
            )
            
            # 检查是否是今天
            today = datetime.datetime.now()
            if current_date.date() == today.date():
                date_btn.config(style='Today.TButton')
            
            # 检查是否是当前月份
            if current_date.month != month:
                date_btn.config(state=tk.DISABLED)
            
            # 检查是否有任务
            date_str = current_date.strftime("%Y-%m-%d")
            has_task = any(task['date'] == date_str for task in self.tasks)
            if has_task:
                date_btn.config(style='Task.TButton')
            
            # 检查是否是选中的日期
            if self.selected_date == date_str:
                date_btn.config(style='Selected.TButton')
            
            date_btn.grid(row=row, column=col, sticky=tk.NSEW, padx=2, pady=2)
        
        # 配置网格权重
        for i in range(7):
            self.calendar_grid.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.calendar_grid.grid_rowconfigure(i, weight=1)
    
    def select_date(self, date):
        self.selected_date = date.strftime("%Y-%m-%d")
        self.render_calendar()
        self.render_tasks()
    
    def prev_month(self):
        self.current_date = self.current_date - datetime.timedelta(days=1)
        self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
        self.render_calendar()
    
    def next_month(self):
        self.current_date = self.current_date + datetime.timedelta(days=32)
        self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
        self.render_calendar()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.settings = data.get('settings', {
                        'work_time': 1500,
                        'short_break': 300,
                        'long_break': 900,
                        'reminder': 'none'
                    })
                    self.remaining_time = self.settings['work_time']
            except Exception as e:
                print(f"加载数据失败: {e}")
    
    def save_data(self):
        try:
            data = {
                'tasks': self.tasks,
                'settings': self.settings
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # 设置窗口图标
    try:
        # 尝试设置图标，即使失败也不会影响程序运行
        pass
    except:
        pass
    
    # 创建自定义样式
    style = ttk.Style()
    
    # 主题设置
    style.theme_use('clam')
    
    # 主窗口背景
    root.configure(bg='#f5f5f5')
    
    # 颜色定义
    colors = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#f093fb',
        'success': '#4CAF50',
        'danger': '#f5576c',
        'background': '#f5f5f5',
        'card_bg': '#ffffff',
        'text': '#333333',
        'text_light': '#999999'
    }
    
    # 自定义样式
    style.configure('TFrame', background=colors['background'])
    style.configure('TLabel', background=colors['background'], font=('Helvetica', 10), foreground=colors['text'])
    style.configure('TButton', font=('Helvetica', 10), padding=5, foreground=colors['text'])
    style.configure('TLabelframe', background=colors['background'], font=('Helvetica', 12, 'bold'))
    style.configure('TLabelframe.Label', background=colors['background'])
    
    # 卡片样式
    style.configure('Card.TFrame', 
                   background=colors['card_bg'],
                   relief='flat',
                   padding=10)
    
    # 标题样式
    style.configure('Title.TLabel', 
                   font=('Helvetica', 16, 'bold'),
                   background=colors['card_bg'],
                   foreground=colors['text'])
    
    # 模式按钮样式
    style.configure('Mode.TButton', 
                   font=('Helvetica', 10, 'bold'),
                   padding=10,
                   foreground=colors['text'],
                   background=colors['background'])
    style.map('Mode.TButton', 
              background=[('active', colors['primary']), ('!active', colors['background'])],
              foreground=[('active', 'white'), ('!active', colors['text'])])
    
    # 控制按钮样式
    style.configure('Control.TButton', 
                   font=('Helvetica', 10, 'bold'),
                   padding=10,
                   foreground='white',
                   background=colors['primary'])
    style.map('Control.TButton', 
              background=[('active', '#5a67d8'), ('!active', colors['primary'])])
    
    # 设置按钮样式
    style.configure('Settings.TButton', 
                   font=('Helvetica', 10),
                   padding=8,
                   foreground=colors['text'],
                   background=colors['background'])
    style.map('Settings.TButton', 
              background=[('active', colors['primary']), ('!active', colors['background'])],
              foreground=[('active', 'white'), ('!active', colors['text'])])
    
    # 输入框样式
    style.configure('TaskInput.TEntry', 
                   font=('Helvetica', 10),
                   padding=10,
                   relief='flat',
                   fieldbackground=colors['background'],
                   foreground=colors['text'])
    
    # 添加任务按钮样式
    style.configure('AddTask.TButton', 
                   font=('Helvetica', 10, 'bold'),
                   padding=10,
                   foreground='white',
                   background=colors['success'])
    style.map('AddTask.TButton', 
              background=[('active', '#388e3c'), ('!active', colors['success'])])
    
    # 操作按钮样式
    style.configure('Action.TButton', 
                   font=('Helvetica', 10),
                   padding=8,
                   foreground='white',
                   background=colors['primary'])
    style.map('Action.TButton', 
              background=[('active', '#5a67d8'), ('!active', colors['primary'])])
    
    # 删除按钮样式
    style.configure('Delete.TButton', 
                   font=('Helvetica', 10),
                   padding=8,
                   foreground='white',
                   background=colors['danger'])
    style.map('Delete.TButton', 
              background=[('active', '#d32f2f'), ('!active', colors['danger'])])
    
    # 导航按钮样式
    style.configure('Nav.TButton', 
                   font=('Helvetica', 10),
                   padding=8,
                   foreground=colors['text'],
                   background=colors['background'])
    style.map('Nav.TButton', 
              background=[('active', colors['primary']), ('!active', colors['background'])],
              foreground=[('active', 'white'), ('!active', colors['text'])])
    
    # 日历标题样式
    style.configure('CalendarTitle.TLabel', 
                   font=('Helvetica', 16, 'bold'),
                   background=colors['card_bg'],
                   foreground=colors['text'])
    
    # 设置框架样式
    style.configure('Setting.TFrame', 
                   background=colors['card_bg'])
    
    # 设置标签样式
    style.configure('Label.TLabel', 
                   font=('Helvetica', 11),
                   background=colors['card_bg'],
                   foreground=colors['text'])
    
    # 设置输入框样式
    style.configure('SettingEntry.TEntry', 
                   font=('Helvetica', 10),
                   padding=8,
                   relief='flat',
                   fieldbackground=colors['background'],
                   foreground=colors['text'])
    
    # 设置下拉框样式
    style.configure('SettingCombobox.TCombobox', 
                   font=('Helvetica', 10),
                   padding=8,
                   relief='flat',
                   fieldbackground=colors['background'],
                   foreground=colors['text'])
    
    # 保存按钮样式
    style.configure('Save.TButton', 
                   font=('Helvetica', 11, 'bold'),
                   padding=12,
                   foreground='white',
                   background=colors['primary'])
    style.map('Save.TButton', 
              background=[('active', '#5a67d8'), ('!active', colors['primary'])])
    
    # 时间显示样式
    style.configure('Time.TLabel', 
                   font=('Helvetica', 48, 'bold'),
                   background=colors['card_bg'],
                   foreground=colors['primary'])
    
    # 今天按钮样式
    style.configure('Today.TButton', 
                   foreground='white', 
                   background=colors['primary'], 
                   font=('Helvetica', 10, 'bold'),
                   padding=5)
    style.map('Today.TButton', 
              background=[('active', '#5a67d8'), ('!active', colors['primary'])])
    
    # 有任务按钮样式
    style.configure('Task.TButton', 
                   foreground='black', 
                   background=colors['accent'],
                   font=('Helvetica', 10),
                   padding=5)
    style.map('Task.TButton', 
              background=[('active', colors['danger']), ('!active', colors['accent'])])
    
    # 选中日期按钮样式
    style.configure('Selected.TButton', 
                   foreground='white', 
                   background=colors['success'], 
                   font=('Helvetica', 10, 'bold'),
                   padding=5)
    style.map('Selected.TButton', 
              background=[('active', '#388e3c'), ('!active', colors['success'])])
    
    # 时间显示框架样式
    style.configure('TimeDisplay.TFrame', 
                   background=colors['card_bg'])
    
    # 输入框架样式
    style.configure('Input.TFrame', 
                   background=colors['card_bg'])
    
    # 列表框架样式
    style.configure('List.TFrame', 
                   background=colors['card_bg'])
    
    # 滚动条样式
    # 为垂直滚动条设置样式
    style.configure('Vertical.TScrollbar', 
                   background=colors['background'],
                   troughcolor=colors['background'],
                   darkcolor=colors['primary'],
                   lightcolor=colors['primary'])
    
    # 为水平滚动条设置样式
    style.configure('Horizontal.TScrollbar', 
                   background=colors['background'],
                   troughcolor=colors['background'],
                   darkcolor=colors['primary'],
                   lightcolor=colors['primary'])
    
    # 任务树样式
    style.configure('TaskTree.Treeview', 
                   font=('Helvetica', 10),
                   background=colors['card_bg'],
                   foreground=colors['text'])
    style.configure('TaskTree.Treeview.Heading', 
                   font=('Helvetica', 10, 'bold'),
                   background=colors['primary'],
                   foreground='white')
    
    # 日历头部样式
    style.configure('CalendarHeader.TFrame', 
                   background=colors['card_bg'])
    
    # 日历网格样式
    style.configure('CalendarGrid.TFrame', 
                   background=colors['card_bg'])
    
    app = PomodoroApp(root)
    root.mainloop()

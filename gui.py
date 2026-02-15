import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
import os

class PlayerSearcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("实况足球 '况两把' 智能筛选器")
        self.root.geometry("1300x900")
        
        # 初始化数据
        self.df = None
        self.excel_file = r"D:\vscode\learn\kuangyiba\况两把.xlsx"
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 自动加载数据
        self.load_data()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
    
    def load_data(self):
        """加载球员数据"""
        try:
            if not os.path.exists(self.excel_file):
                messagebox.showerror("错误", f"找不到数据库文件：{self.excel_file}")
                return
            
            self.df = pd.read_excel(self.excel_file)
            
            # 重命名列名，使更符合习惯
            column_mapping = {
                '球员': '姓名',
                '背号': '号码',
                '俱乐部': '球队',
                '惯用脚': '惯用脚'
            }
            self.df = self.df.rename(columns=column_mapping)
            
            # 确保所有列都存在
            required_columns = ['姓名', '位置', '类型', '号码', '球队', '国籍', '身高', '惯用脚']
            for col in required_columns:
                if col not in self.df.columns:
                    messagebox.showwarning("警告", f"数据库缺少列：{col}")
            
            # 将号码列转换为数值类型（处理可能的NaN值）
            if '号码' in self.df.columns:
                self.df['号码'] = pd.to_numeric(self.df['号码'], errors='coerce')
            
            self.status_label.config(
                text=f"✓ 数据加载成功！共 {len(self.df)} 名球员", 
                foreground="green"
            )
            
            self.update_fields_list()
            self.update_quick_conditions()
            
        except Exception as e:
            self.df = pd.DataFrame()
            self.status_label.config(
                text=f"✗ 数据加载失败: {str(e)}", 
                foreground="red"
            )
            messagebox.showerror("错误", f"加载数据时出错：{str(e)}")
    
    def update_fields_list(self):
        """更新数据库字段列表"""
        if not self.df.empty:
            fields = list(self.df.columns)
            self.fields_listbox.delete(0, tk.END)
            for field in fields:
                self.fields_listbox.insert(tk.END, field)
    
    def update_quick_conditions(self):
        """根据数据更新快速条件"""
        if not self.df.empty:
            # 获取热门国籍
            top_nationalities = self.df['国籍'].value_counts().head(10).index.tolist()
            
            # 更新国籍按钮
            for i, nationality in enumerate(top_nationalities):
                if i < len(self.nationality_buttons):
                    self.nationality_buttons[i].config(
                        text=nationality, 
                        command=lambda n=nationality: self.add_condition(n)
                    )
            
            # 获取热门球队
            top_clubs = self.df['球队'].value_counts().head(8).index.tolist()
            
            # 更新球队按钮
            for i, club in enumerate(top_clubs):
                if i < len(self.club_buttons):
                    display_name = club[:10] + "..." if len(club) > 10 else club
                    self.club_buttons[i].config(
                        text=display_name,
                        command=lambda c=club: self.add_condition(c)
                    )
    
    def create_widgets(self):
        """创建界面组件"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题栏
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="⚽ 实况足球 '况两把' 智能筛选器", 
            font=("微软雅黑", 18, "bold"),
            foreground="#2196F3"
        )
        title_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(
            title_frame, 
            text="准备加载数据...", 
            font=("微软雅黑", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        refresh_btn = ttk.Button(
            title_frame, 
            text="刷新数据", 
            command=self.load_data,
            width=10
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # 左侧面板
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # 输入框区域
        input_frame = ttk.LabelFrame(left_panel, text="🔍 搜索条件", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        
        ttk.Label(input_frame, text="输入线索:", font=("微软雅黑", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_container = ttk.Frame(input_frame)
        input_container.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_container.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_container, font=("微软雅黑", 11))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self.search_players())
        
        search_btn = ttk.Button(
            input_container, 
            text="搜索", 
            command=self.search_players,
            width=8
        )
        search_btn.grid(row=0, column=1, padx=(0, 5))
        
        clear_btn = ttk.Button(
            input_container, 
            text="清除", 
            command=self.clear_results,
            width=8
        )
        clear_btn.grid(row=0, column=2)
        
        # 输入提示
        help_text = """格式说明（支持不全信息）：
• 精确匹配: =前缀（如 =163 或 =巴西 或 =10）
• 范围匹配: > 或 <（如 >180 或 <30 或 <6）
• 区间匹配: 数字-数字（如 170-175 或 5-15）
• 接近匹配: 直接数字（如 163）
• 文本匹配: 直接文字（如 巴西 或 中锋）

示例:
• 巴西 巴萨      → 巴西籍巴萨球员
• 中锋 170       → 中锋身高接近170cm
• 皇马 >180      → 皇马身高>180cm球员
• 法国 <10       → 法国籍号码<10球员
• 10-20 巴西     → 号码10-20巴西球员"""
        
        help_label = ttk.Label(
            input_frame, 
            text=help_text, 
            justify=tk.LEFT,
            font=("微软雅黑", 8),
            foreground="#666"
        )
        help_label.grid(row=2, column=0, sticky=tk.W)
        
        # 快速条件 - 国籍
        nationality_frame = ttk.LabelFrame(left_panel, text="🌍 热门国籍", padding="8")
        nationality_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        
        self.nationality_buttons = []
        for i in range(10):
            btn = ttk.Button(nationality_frame, text=f"国籍{i+1}", width=8)
            btn.grid(row=i//5, column=i%5, padx=2, pady=2)
            self.nationality_buttons.append(btn)
        
        # 快速条件 - 球队
        club_frame = ttk.LabelFrame(left_panel, text="🏆 热门球队", padding="8")
        club_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        
        self.club_buttons = []
        for i in range(8):
            btn = ttk.Button(club_frame, text=f"球队{i+1}", width=12)
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
            self.club_buttons.append(btn)
        
        # 快速条件 - 位置
        position_frame = ttk.LabelFrame(left_panel, text="📍 位置筛选", padding="8")
        position_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        
        positions = ["中锋", "影锋", "边锋", "前腰", "中前卫", "后腰", "中后卫", "边后卫", "门将"]
        for i, pos in enumerate(positions):
            btn = ttk.Button(
                position_frame, 
                text=pos, 
                width=8,
                command=lambda p=pos: self.add_condition(p)
            )
            btn.grid(row=i//5, column=i%5, padx=2, pady=2)
        
        # 快速条件 - 身高范围
        height_frame = ttk.LabelFrame(left_panel, text="📏 身高筛选", padding="8")
        height_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        
        height_buttons = [
            ("<170", "<170"), ("170-175", "170-175"), ("176-180", "176-180"),
            ("181-185", "181-185"), (">185", ">185"), ("常见163", "=163")
        ]
        
        for i, (text, cmd) in enumerate(height_buttons):
            btn = ttk.Button(
                height_frame, 
                text=text, 
                width=9,
                command=lambda c=cmd: self.add_condition(c)
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
        
        # 快速条件 - 号码范围
        number_frame = ttk.LabelFrame(left_panel, text="🔢 号码筛选", padding="8")
        number_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        
        number_buttons = [
            ("号码<6", "<6"), ("号码<10", "<10"), ("号码10-20", "10-20"),
            ("号码>20", ">20"), ("号码1-5", "1-5"), ("号码<30", "<30")
        ]
        
        for i, (text, cmd) in enumerate(number_buttons):
            btn = ttk.Button(
                number_frame, 
                text=text, 
                width=9,
                command=lambda c=cmd: self.add_condition(c)
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
        
        # 数据库字段列表
        fields_frame = ttk.LabelFrame(left_panel, text="📋 数据库字段", padding="10")
        fields_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        fields_frame.rowconfigure(0, weight=1)
        fields_frame.columnconfigure(0, weight=1)
        
        self.fields_listbox = tk.Listbox(
            fields_frame, 
            height=8,
            font=("Consolas", 9),
            bg="white",
            selectbackground="#2196F3"
        )
        self.fields_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(fields_frame, orient=tk.VERTICAL, command=self.fields_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.fields_listbox.config(yscrollcommand=scrollbar.set)
        
        # 中间面板 - 搜索结果
        middle_panel = ttk.Frame(main_frame)
        middle_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        middle_panel.columnconfigure(0, weight=1)
        middle_panel.rowconfigure(1, weight=1)
        
        # 结果统计
        stats_frame = ttk.Frame(middle_panel)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.result_count_label = ttk.Label(
            stats_frame, 
            text="准备就绪", 
            font=("微软雅黑", 11, "bold")
        )
        self.result_count_label.pack(side=tk.LEFT)
        
        self.conditions_label = ttk.Label(
            stats_frame, 
            text="",
            font=("微软雅黑", 9),
            foreground="#666"
        )
        self.conditions_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 结果表格
        columns = ("姓名", "国籍", "球队", "位置", "身高", "号码", "类型", "惯用脚")
        
        tree_frame = ttk.Frame(middle_panel)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings",
            height=22,
            selectmode="browse"
        )
        
        column_widths = {"姓名": 100, "国籍": 80, "球队": 120, "位置": 60, 
                        "身高": 60, "号码": 60, "类型": 60, "惯用脚": 60}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 右侧面板
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # 详细信息
        detail_frame = ttk.LabelFrame(right_panel, text="👤 球员详情", padding="10")
        detail_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        self.detail_text = scrolledtext.ScrolledText(
            detail_frame, 
            width=35,
            height=22,
            font=("微软雅黑", 10),
            bg="#f8f9fa",
            wrap=tk.WORD
        )
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 统计数据
        stats_detail_frame = ttk.LabelFrame(right_panel, text="📊 统计信息", padding="10")
        stats_detail_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(10, 0))
        
        self.stats_label = ttk.Label(
            stats_detail_frame, 
            text="暂无数据",
            font=("微软雅黑", 9)
        )
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # 底部面板 - 日志
        bottom_panel = ttk.LabelFrame(main_frame, text="📝 筛选日志", padding="10")
        bottom_panel.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_panel.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            bottom_panel, 
            height=4,
            font=("Consolas", 9),
            bg="#f5f5f5"
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.show_player_details())
        self.input_entry.focus_set()
    
    def add_condition(self, condition):
        """添加条件到输入框"""
        current = self.input_entry.get()
        if current:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, f"{current} {condition}")
        else:
            self.input_entry.insert(0, condition)
        self.input_entry.focus()
    
    def parse_input(self, user_input):
        """智能解析输入条件（支持身高和号码范围）"""
        conditions = []
        parts = user_input.split()
        
        for part in parts:
            # 处理范围条件（如170-175或5-15）
            if '-' in part and part.replace('-', '').isdigit():
                try:
                    start, end = map(int, part.split('-'))
                    # 根据数值范围判断是身高还是号码
                    if 150 <= start <= 230 and 150 <= end <= 230:  # 身高范围
                        conditions.append({'field': '身高', 'value': (start, end), 'type': 'range'})
                    elif 1 <= start <= 99 and 1 <= end <= 99:     # 号码范围
                        conditions.append({'field': '号码', 'value': (start, end), 'type': 'range'})
                    continue
                except:
                    pass
            
            # 精确匹配（以=开头）
            if part.startswith('='):
                value = part[1:]
                if value.isdigit():
                    num = int(value)
                    if 150 <= num <= 230:  # 身高
                        conditions.append({'field': '身高', 'value': num, 'type': 'exact'})
                    elif 1 <= num <= 99:   # 号码
                        conditions.append({'field': '号码', 'value': num, 'type': 'exact'})
                else:
                    field = self.guess_field_type(value)
                    conditions.append({'field': field, 'value': value, 'type': 'exact'})
            
            # 大于匹配
            elif part.startswith('>'):
                value = part[1:]
                if value.isdigit():
                    num = int(value)
                    if 150 <= num <= 230:  # 身高
                        conditions.append({'field': '身高', 'value': num, 'type': 'greater'})
                    elif 1 <= num <= 99:   # 号码
                        conditions.append({'field': '号码', 'value': num, 'type': 'greater'})
            
            # 小于匹配
            elif part.startswith('<'):
                value = part[1:]
                if value.isdigit():
                    num = int(value)
                    if 150 <= num <= 230:  # 身高
                        conditions.append({'field': '身高', 'value': num, 'type': 'less'})
                    elif 1 <= num <= 99:   # 号码
                        conditions.append({'field': '号码', 'value': num, 'type': 'less'})
            
            # 数字匹配（接近匹配）
            elif part.isdigit():
                num = int(part)
                if 150 <= num <= 230:  # 身高范围
                    conditions.append({'field': '身高', 'value': num, 'type': 'close'})
                elif 1 <= num <= 99:   # 号码范围
                    conditions.append({'field': '号码', 'value': num, 'type': 'close'})
            
            # 文本匹配
            else:
                field = self.guess_field_type(part)
                conditions.append({'field': field, 'value': part, 'type': 'contain'})
        
        return conditions
    
    def guess_field_type(self, value):
        """智能猜测字段类型"""
        if not self.df.empty:
            # 检查是否是国籍
            if '国籍' in self.df.columns:
                unique_nationalities = self.df['国籍'].astype(str).str.lower().unique()
                if str(value).lower() in unique_nationalities:
                    return '国籍'
            
            # 检查是否是球队
            if '球队' in self.df.columns:
                unique_clubs = self.df['球队'].astype(str).str.lower().unique()
                if str(value).lower() in unique_clubs:
                    return '球队'
            
            # 检查是否是位置（关键词匹配）
            position_keywords = ['锋', '卫', '门', '腰', '边', '前', '后', '中场']
            if any(keyword in value for keyword in position_keywords):
                return '位置'
            
            # 检查是否是类型
            if '类型' in self.df.columns and value in ['现役', '历史']:
                return '类型'
            
            # 检查是否是惯用脚
            if '惯用脚' in self.df.columns and value in ['左', '右']:
                return '惯用脚'
        
        # 默认猜测为国籍
        return '国籍'
    
    def advanced_search(self, conditions):
        """执行高级搜索（支持身高和号码范围）"""
        result = self.df.copy()
        log_messages = []
        
        for condition in conditions:
            field = condition['field']
            value = condition['value']
            match_type = condition['type']
            
            if field not in self.df.columns:
                log_messages.append(f"⚠️ 字段不存在: '{field}'")
                continue
            
            before_count = len(result)
            
            if match_type == 'exact':
                # 精确匹配
                if self.df[field].dtype in ['int64', 'float64']:
                    result = result[result[field] == value]
                    log_messages.append(f"🟢 {field} = {value}: {before_count} → {len(result)} 人")
                else:
                    result = result[result[field].astype(str) == str(value)]
                    log_messages.append(f"🟢 {field} = '{value}': {before_count} → {len(result)} 人")
            
            elif match_type == 'close':
                # 接近匹配（±5）
                if self.df[field].dtype in ['int64', 'float64']:
                    result = result[abs(result[field] - value) <= 5]
                    log_messages.append(f"🔵 {field} ≈ {value} (±5): {before_count} → {len(result)} 人")
                else:
                    result = result[result[field].astype(str).str.contains(str(value), case=False, na=False)]
                    log_messages.append(f"🔵 {field} 包含 '{value}': {before_count} → {len(result)} 人")
            
            elif match_type == 'contain':
                # 包含匹配
                result = result[result[field].astype(str).str.contains(str(value), case=False, na=False)]
                log_messages.append(f"🔵 {field} 包含 '{value}': {before_count} → {len(result)} 人")
            
            elif match_type == 'greater':
                # 大于
                if self.df[field].dtype in ['int64', 'float64']:
                    result = result[result[field] > value]
                    log_messages.append(f"🔼 {field} > {value}: {before_count} → {len(result)} 人")
            
            elif match_type == 'less':
                # 小于
                if self.df[field].dtype in ['int64', 'float64']:
                    result = result[result[field] < value]
                    log_messages.append(f"🔽 {field} < {value}: {before_count} → {len(result)} 人")
            
            elif match_type == 'range':
                # 范围匹配（适用于身高和号码）
                start, end = value
                if self.df[field].dtype in ['int64', 'float64']:
                    result = result[(result[field] >= start) & (result[field] <= end)]
                    log_messages.append(f"📏 {field} {start}-{end}: {before_count} → {len(result)} 人")
            
            # 如果筛选后为空，提前结束
            if len(result) == 0:
                log_messages.append(f"❌ 筛选后无结果，停止后续筛选")
                break
        
        return result, log_messages
    
    def search_players(self):
        """执行搜索"""
        if self.df is None or self.df.empty:
            messagebox.showerror("错误", "请先加载球员数据库！")
            return
        
        user_input = self.input_entry.get().strip()
        if not user_input:
            messagebox.showinfo("提示", "请输入搜索条件！")
            return
        
        try:
            conditions = self.parse_input(user_input)
            
            if not conditions:
                messagebox.showwarning("警告", "未能识别到有效条件！")
                return
            
            # 显示条件
            cond_text = " | ".join([
                f"{c['field']} {c['type']} {c['value']}" 
                for c in conditions
            ])
            self.conditions_label.config(text=f"条件: {cond_text}")
            
            # 执行搜索
            result, log_messages = self.advanced_search(conditions)
            
            # 更新结果统计
            self.result_count_label.config(
                text=f"找到 {len(result)} 名球员",
                foreground="green" if len(result) > 0 else "red"
            )
            
            # 显示日志
            self.log_text.delete(1.0, tk.END)
            for log in log_messages:
                self.log_text.insert(tk.END, f"{log}\n")
            
            # 清空表格
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            # 填充表格
            if not result.empty:
                for idx, row in result.iterrows():
                    values = [
                        row.get('姓名', ''),
                        row.get('国籍', ''),
                        row.get('球队', ''),
                        row.get('位置', ''),
                        row.get('身高', ''),
                        row.get('号码', ''),
                        row.get('类型', ''),
                        row.get('惯用脚', '')
                    ]
                    self.tree.insert("", tk.END, values=values)
                
                # 更新统计信息
                self.update_statistics(result)
                
                # 自动选择第一行
                if self.tree.get_children():
                    first_item = self.tree.get_children()[0]
                    self.tree.selection_set(first_item)
                    self.tree.focus(first_item)
                    self.show_player_details()
            else:
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, "未找到符合条件的球员")
                self.stats_label.config(text="无统计数据")
                
        except Exception as e:
            messagebox.showerror("错误", f"搜索时出错：{str(e)}")
    
    def update_statistics(self, result):
        """更新统计信息"""
        stats_text = ""
        
        if '身高' in result.columns and not result.empty:
            stats_text += f"身高统计:\n"
            stats_text += f"• 最高: {result['身高'].max()}cm\n"
            stats_text += f"• 最低: {result['身高'].min()}cm\n"  
            stats_text += f"• 平均: {result['身高'].mean():.1f}cm\n"
            stats_text += f"• 中位数: {result['身高'].median()}cm\n\n"
        
        if '号码' in result.columns and not result.empty:
            # 过滤掉NaN值
            numbers = result['号码'].dropna()
            if len(numbers) > 0:
                stats_text += f"号码统计:\n"
                stats_text += f"• 最小号码: {int(numbers.min())}\n"
                stats_text += f"• 最大号码: {int(numbers.max())}\n"
                stats_text += f"• 平均号码: {numbers.mean():.1f}\n\n"
        
        if '国籍' in result.columns and not result.empty:
            top_countries = result['国籍'].value_counts().head(3)
            if not top_countries.empty:
                stats_text += "国籍分布:\n"
                for country, count in top_countries.items():
                    stats_text += f"• {country}: {count}人\n"
                stats_text += "\n"
        
        if '球队' in result.columns and not result.empty:
            top_clubs = result['球队'].value_counts().head(3)
            if not top_clubs.empty:
                stats_text += "球队分布:\n"
                for club, count in top_clubs.items():
                    stats_text += f"• {club}: {count}人\n"
        
        self.stats_label.config(text=stats_text if stats_text else "无统计数据")
    
    def show_player_details(self):
        """显示选定球员的详细信息"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        player_name = item['values'][0]
        
        if not self.df.empty and '姓名' in self.df.columns:
            player_data = self.df[self.df['姓名'] == player_name]
            if not player_data.empty:
                player_data = player_data.iloc[0]
                
                detail_text = f"【球员详情】\n{'='*30}\n"
                detail_text += f"姓名: {player_data.get('姓名', 'N/A')}\n"
                detail_text += f"国籍: {player_data.get('国籍', 'N/A')}\n"
                detail_text += f"球队: {player_data.get('球队', 'N/A')}\n"
                detail_text += f"位置: {player_data.get('位置', 'N/A')}\n"
                detail_text += f"身高: {player_data.get('身高', 'N/A')}cm\n"
                detail_text += f"号码: {player_data.get('号码', 'N/A')}\n"
                detail_text += f"类型: {player_data.get('类型', 'N/A')}\n"
                detail_text += f"惯用脚: {player_data.get('惯用脚', 'N/A')}\n"
                
                # 添加其他字段
                shown_fields = ['姓名', '国籍', '球队', '位置', '身高', '号码', '类型', '惯用脚']
                other_fields = [f for f in self.df.columns if f not in shown_fields]
                
                if other_fields:
                    detail_text += f"\n{'='*30}\n【其他信息】\n"
                    for field in other_fields:
                        value = player_data.get(field, '')
                        if pd.notna(value) and str(value).strip():
                            detail_text += f"{field}: {value}\n"
                
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, detail_text)
    
    def clear_results(self):
        """清除搜索结果"""
        self.input_entry.delete(0, tk.END)
        self.result_count_label.config(text="准备就绪", foreground="black")
        self.conditions_label.config(text="")
        self.detail_text.delete(1.0, tk.END)
        self.stats_label.config(text="暂无数据")
        self.log_text.delete(1.0, tk.END)
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.input_entry.focus_set()

def main():
    """主函数"""
    root = tk.Tk()
    
    window_width = 1300
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    app = PlayerSearcherGUI(root)
    
    root.bind('<Escape>', lambda e: root.quit())
    
    root.mainloop()

if __name__ == "__main__":
    main()
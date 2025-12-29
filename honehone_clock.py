import sys
import json
import datetime
import os
from PyQt6.QtWidgets import QApplication, QWidget, QMenu, QMessageBox, QDialog, QVBoxLayout, QLabel, QColorDialog
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPixmap, QPainter, QImage, QAction, QColor
from PIL import Image

# 获取资源路径（兼容PyInstaller打包）
def resource_path(relative_path):
    try:
        # PyInstaller创建临时文件夹的路径
        base_path = sys._MEIPASS
    except Exception:
        # 正常开发环境下的路径
        # 获取当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class HoneHoneClock(QWidget):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标志：无边框、总是在最前面、不显示在任务栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        
        
        # 确保窗口可见
        self.setAutoFillBackground(False)
        
        # 设置窗口图标
        from PyQt6.QtGui import QIcon
        icon_path = resource_path('attest/logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 主题设置
        self.themes = [
            {"key": "default", "name": "默认"},
            {"key": "black", "name": "黑色"},
            {"key": "white", "name": "白色"},
            {"key": "red", "name": "红色"},
            {"key": "blue", "name": "蓝色"}
        ]
        self.current_theme = "default"
        
        # 背景颜色和透明度设置
        self.background_color = "transparent"  # 默认透明背景
        self.background_opacity = 1.0  # 默认不透明（1.0表示完全不透明，0.0表示完全透明）
        self.available_colors = {
            "透明": "transparent",
            "白色": "white",
            "红色": "red",
            "蓝色": "blue",
            "绿色": "green",
            "黄色": "yellow",
            "紫色": "purple",
            "橙色": "orange",
            "黑色": "black",
            "灰色": "gray"
        }
        
        # 设置透明背景属性
        if self.background_color == "transparent":
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 分隔符设置
        self.colon_blinking = True  # 分隔符是否闪烁
        
        # 加载资源
        self.sprite_sheet = None
        self.frame_rects = []
        self.frame_pixmaps = []
        # 初始化ani_data为完整的数字动画数据，即使资源加载失败也能防止索引错误
        self.ani_data = [
            {"prefix": "0", "count": 6, "frame_from": 0, "frame_to": 0},
            {"prefix": "1", "count": 9, "frame_from": 0, "frame_to": 0},
            {"prefix": "2", "count": 7, "frame_from": 0, "frame_to": 0},
            {"prefix": "3", "count": 6, "frame_from": 0, "frame_to": 0},
            {"prefix": "4", "count": 9, "frame_from": 0, "frame_to": 0},
            {"prefix": "5", "count": 14, "frame_from": 0, "frame_to": 0},
            {"prefix": "6", "count": 7, "frame_from": 0, "frame_to": 0},
            {"prefix": "7", "count": 10, "frame_from": 0, "frame_to": 0},
            {"prefix": "8", "count": 7, "frame_from": 0, "frame_to": 0},
            {"prefix": "9", "count": 9, "frame_from": 0, "frame_to": 0},
            {"prefix": "colon", "count": 4, "frame_from": 0, "frame_to": 0}  # 分隔符动画数据
        ]
        self.load_resources()
        
        # 时钟组件
        self.clock_hour1 = ClockDigit(self)
        self.clock_hour2 = ClockDigit(self)
        self.clock_colon1 = ClockDigit(self)  # 时分分隔符
        self.clock_min1 = ClockDigit(self)
        self.clock_min2 = ClockDigit(self)
        self.clock_colon2 = ClockDigit(self)  # 分秒分隔符
        self.clock_sec1 = ClockDigit(self)
        self.clock_sec2 = ClockDigit(self)
        
        # 初始化分隔符
        self.clock_colon1.set_number(10)  # 设置为分隔符
        self.clock_colon2.set_number(10)  # 设置为分隔符
        
        # 位置配置（使用相对比例，基于原始窗口大小750x250）
        self.digit_positions = [
            (50/750, 200/250),    # hour1
            (150/750, 200/250),   # hour2
            (225/750, 200/250),   # colon1（时分中间）
            (300/750, 200/250),   # min1
            (400/750, 200/250),   # min2
            (475/750, 200/250),   # colon2（分秒中间）
            (550/750, 200/250),   # sec1
            (650/750, 200/250)    # sec2
        ]
        
        # 动画控制
        self.current_time = None
        self.last_update_time = 0
        self.animation_speed = 1.0  # 每秒播放的完整序列数，确保4帧动画每秒完成一次循环
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frames)
        self.frame_timer.start(int(1000 / 60))  # 60 FPS
        
        # 时间更新计时器
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # 每秒更新一次
        
        # 初始化
        self.update_time()
        
        # 调整窗口大小以适应所有数字和动画帧
        self.resize(750, 250)
        
        # 将窗口移动到屏幕中央（更靠近屏幕顶部，确保可见）
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = 100  # 固定在屏幕顶部下方100像素处，避免被任务栏或其他窗口遮挡
        self.move(x, y)
        

        
        # 初始化时根据默认背景颜色设置透明属性
        self.change_background_color(self.background_color)
        
        # 缩放相关属性
        self.original_width = 750
        self.original_height = 250
        self.scale_factor = 1.0  # 缩放因子，1.0为原始大小
        self.min_scale = 0.1  # 最小缩放比例（10%）
        self.max_scale = 2.0  # 最大缩放比例（200%）
        self.aspect_ratio = self.original_width / self.original_height  # 宽高比
        
        # 置顶状态
        self.is_always_on_top = True  # 默认开启置顶
        
        # 确保窗口不透明
        self.setWindowOpacity(1.0)
        
        # 显示窗口
        self.show()
        
        # 强制激活和显示窗口
        self.activateWindow()
        self.raise_()
        
    
    def load_resources(self):
        # 清空现有资源
        self.frame_rects.clear()
        self.frame_pixmaps.clear()
        self.sprite_sheet = None
        
        # 根据当前主题加载精灵图
        sprite_path = resource_path(f'theme/{self.current_theme}.png')
        try:
            self.sprite_sheet = Image.open(sprite_path)
        except Exception as e:
            # 如果主题图片加载失败，尝试加载默认图片
            try:
                sprite_path = resource_path('HoneHoneClock.png')
                self.sprite_sheet = Image.open(sprite_path)
            except Exception as e2:
                return
        
        # 加载JSON配置
        json_path = resource_path('config.json')
        data = None
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            # 尝试使用二进制模式读取并解码
            try:
                with open(json_path, 'rb') as f:
                    content = f.read().decode('utf-8')
                    data = json.loads(content)
            except Exception as e2:
                return
        
        # 更新动画数据的frame_from和frame_to
        # ani_data已经在__init__中初始化，这里只需要更新frame_from和frame_to
        
        # 确保frames是dict类型
        if 'frames' not in data:
            return
        
        frames = data['frames']
        
        # 如果frames是字节类型，尝试解码
        if isinstance(frames, bytes):
            try:
                frames = json.loads(frames.decode('utf-8'))
            except Exception as e:
                return
        
        if not isinstance(frames, dict):
            return
        
        # 预加载所有帧为QPixmap
        k = 0
        colon_frames_loaded = 0
        for i in range(len(self.ani_data)):
            data_item = self.ani_data[i]
            data_item["frame_from"] = k
            for j in range(1, data_item["count"] + 1):
                frame_name = f"{data_item['prefix']}({j}).png"
                if frame_name in frames:
                    frame_info = frames[frame_name]['frame']
                    rect = (frame_info['x'], frame_info['y'], 
                           frame_info['x'] + frame_info['w'], 
                           frame_info['y'] + frame_info['h'])
                    
                    # 检查帧坐标是否在精灵图范围内
                    if (rect[0] >= 0 and rect[1] >= 0 and 
                        rect[2] <= self.sprite_sheet.width and 
                        rect[3] <= self.sprite_sheet.height):
                        # 裁剪并转换为QPixmap
                        frame_image = self.sprite_sheet.crop(rect)
                        
                        if frame_image.mode != 'RGBA':
                            frame_image = frame_image.convert('RGBA')
                        
                        data_bytes = frame_image.tobytes('raw', 'RGBA')
                        qimage = QImage(data_bytes, frame_image.width, frame_image.height, QImage.Format.Format_RGBA8888)
                        pixmap = QPixmap.fromImage(qimage)
                        
                        self.frame_rects.append(rect)
                        self.frame_pixmaps.append(pixmap)
                        k += 1
                        if data_item['prefix'] == 'colon':
                            colon_frames_loaded += 1
                    else:
                        pass  # 坐标超出范围
                else:
                    pass  # 未找到frame_name
            data_item["frame_to"] = k - 1
        
        
        
        

        self.sprite_sheet.close()
        self.sprite_sheet = None
    
    def update_time(self):
        now = datetime.datetime.now()
        hours = now.hour
        minutes = now.minute
        seconds = now.second
        
        # 更新小时
        hour1 = hours // 10
        hour2 = hours % 10
        self.clock_hour1.set_number(hour1)
        self.clock_hour2.set_number(hour2)
        
        # 更新分钟
        min1 = minutes // 10
        min2 = minutes % 10
        self.clock_min1.set_number(min1)
        self.clock_min2.set_number(min2)
        
        # 更新秒钟
        sec1 = seconds // 10
        sec2 = seconds % 10
        self.clock_sec1.set_number(sec1)
        self.clock_sec2.set_number(sec2)
        
        self.last_update_time = now.timestamp()
        self.update()
    
    def update_frames(self):
        # 更新所有数字和分隔符的动画帧
        self.clock_hour1.update_frame()
        self.clock_hour2.update_frame()
        self.clock_colon1.update_frame()
        self.clock_min1.update_frame()
        self.clock_min2.update_frame()
        self.clock_colon2.update_frame()
        self.clock_sec1.update_frame()
        self.clock_sec2.update_frame()
        self.repaint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取当前窗口大小
        current_width = self.width()
        current_height = self.height()
        
        # 绘制背景
        if self.background_color != "transparent":
            # 计算不透明度（0-255范围）
            opacity = int(self.background_opacity * 255)
            # 创建带透明度的颜色
            color = QColor(self.background_color)
            color.setAlpha(opacity)
            painter.fillRect(self.rect(), color)
        
        # 绘制所有数字和分隔符
        digits = [self.clock_hour1, self.clock_hour2, self.clock_colon1, 
                 self.clock_min1, self.clock_min2, self.clock_colon2, 
                 self.clock_sec1, self.clock_sec2]
        
        for i, digit in enumerate(digits):
            # 将相对比例转换为实际像素位置
            x_ratio, y_ratio = self.digit_positions[i]
            x = int(x_ratio * current_width)
            y = int(y_ratio * current_height)
            digit.draw(painter, x, y)
        
        
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def wheelEvent(self, event):
        # 鼠标滚轮缩放
        delta = event.angleDelta().y() / 120  # 获取滚轮增量，正负表示方向
        
        # 计算缩放因子变化，每次缩放5%
        scale_change = 0.05
        if delta < 0:
            scale_change = -scale_change
        
        # 计算新的缩放因子并限制在范围内
        new_scale = self.scale_factor + scale_change
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            
            # 计算新的窗口大小，保持宽高比
            new_width = int(self.original_width * self.scale_factor)
            new_height = int(self.original_height * self.scale_factor)
            
            # 保存当前窗口位置
            current_pos = self.pos()
            
            # 调整窗口大小
            self.resize(new_width, new_height)
            
            # 保持窗口中心位置不变
            new_pos_x = current_pos.x() + (self.width() - new_width) // 2
            new_pos_y = current_pos.y() + (self.height() - new_height) // 2
            self.move(new_pos_x, new_pos_y)
            
            event.accept()
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # 设置右键菜单样式，确保在深色主题下文字可见，并适配高分屏
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(50, 50, 50, 255);
                color: white;
                border: 1px solid #777;
                padding: 8px;
                font-family: Microsoft YaHei, sans-serif;
                font-size: 14px;
            }
            QMenu::item {
                background-color: transparent;
                color: white;
                padding: 8px 30px 8px 30px;
                margin: 2px;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QMenu::item:disabled {
                color: #888;
            }
        """)
        
        # 主题切换子菜单
        theme_menu = menu.addMenu("主题切换")
        
        # 添加主题选项
        for theme in self.themes:
            # 设置主题选项文本（使用中文名称）
            theme_text = theme["name"]
            theme_action = theme_menu.addAction(theme_text)
            # 连接主题切换信号
            theme_action.triggered.connect(lambda checked, t=theme["key"]: self.change_theme(t))
            
        menu.addSeparator()  # 添加分隔线
        
        # 添加设置子菜单
        settings_menu = menu.addMenu("设置")
        
        # 在设置子菜单中添加置顶选项
        always_on_top_action = settings_menu.addAction("始终置顶")
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.is_always_on_top)
        always_on_top_action.triggered.connect(self.toggle_always_on_top)
        
        # 添加分隔符闪烁选项
        colon_blink_action = settings_menu.addAction("分隔符闪烁")
        colon_blink_action.setCheckable(True)
        colon_blink_action.setChecked(self.colon_blinking)
        colon_blink_action.triggered.connect(self.toggle_colon_blinking)
        
        # 添加背景颜色设置子菜单
        bg_color_menu = settings_menu.addMenu("背景颜色")
        
        # 添加颜色选项
        for color_name, color_value in self.available_colors.items():
            color_action = bg_color_menu.addAction(color_name)
            color_action.triggered.connect(lambda checked, c=color_value: self.change_background_color(c))
        
        # 添加自定义颜色选择
        bg_color_menu.addSeparator()
        custom_color_action = bg_color_menu.addAction("自定义颜色")
        custom_color_action.triggered.connect(self.select_custom_color)
        
        # 添加透明度调整
        opacity_menu = settings_menu.addMenu("透明度")
        opacity_values = [0.2, 0.4, 0.6, 0.8, 1.0]
        for opacity in opacity_values:
            opacity_action = opacity_menu.addAction(f"{int(opacity * 100)}%")
            opacity_action.triggered.connect(lambda checked, o=opacity: self.change_opacity(o))
        
        menu.addSeparator()  # 添加分隔线
        
        about_action = menu.addAction("关于")
        quit_action = menu.addAction("退出")
        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == about_action:
            self.show_about_dialog()
        elif action == quit_action:
            QApplication.quit()
    
    def get_frame_image(self, frame_index):
        if 0 <= frame_index < len(self.frame_pixmaps):
            return self.frame_pixmaps[frame_index]
        return None
    
    def toggle_always_on_top(self, checked):
        """
        切换窗口置顶状态
        :param checked: 新的置顶状态
        """
        self.is_always_on_top = checked
        
        # 更新窗口标志
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        
        # 重新显示窗口以应用新的窗口标志
        self.show()
    
    def toggle_colon_blinking(self, checked):
        """
        切换分隔符闪烁状态
        :param checked: 新的闪烁状态
        """
        self.colon_blinking = checked
        
        # 如果启用闪烁且分隔符不在播放动画，则开始播放
        if checked and not (self.clock_colon1.is_playing or self.clock_colon2.is_playing):
            self.clock_colon1.is_playing = True
            self.clock_colon2.is_playing = True
        self.update()
    
    def change_background_color(self, color):
        """
        更改窗口背景颜色
        :param color: 新的背景颜色值
        """
        self.background_color = color
        
        if color == "transparent":
            # 启用透明背景
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAutoFillBackground(False)
        else:
            # 禁用透明背景
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            self.setAutoFillBackground(False)
        
        self.update()
    
    def select_custom_color(self):
        """
        打开颜色选择对话框，让用户选择自定义颜色
        """
        # 如果当前背景色不是透明，将其作为初始颜色
        if self.background_color != "transparent":
            initial_color = QColor(self.background_color)
        else:
            initial_color = QColor(255, 255, 255)  # 默认白色
        
        # 打开颜色选择对话框
        color = QColorDialog.getColor(initial_color, self, "选择背景颜色")
        
        if color.isValid():
            # 将选中的颜色转换为十六进制格式
            color_hex = color.name()
            self.change_background_color(color_hex)
    
    def change_opacity(self, opacity):
        """
        调整窗口背景透明度
        :param opacity: 透明度值（0.0-1.0）
        """
        self.background_opacity = opacity
        self.update()
    
    def closeEvent(self, event):
        # 当主窗口关闭时，退出应用程序
        QApplication.quit()
    
    def change_theme(self, theme):
        """
        切换主题
        :param theme: 要切换的主题key
        """
        # 检查主题key是否存在
        theme_exists = any(t["key"] == theme for t in self.themes)
        if theme_exists and theme != self.current_theme:
            self.current_theme = theme
            # 重新加载资源
            self.load_resources()
            # 更新时间显示，确保正确显示当前时间
            self.update_time()
            # 刷新界面
            self.update()
    
    def show_about_dialog(self):
        about_text = """
<p style='font-size:24px; font-weight:bold; color:#0078d7;text-align:center;'>人体时钟 (HoneHone Clock)</p><br><br>
<b>🪜 版&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本:&nbsp;</b> 1.0.0<br>
<b>🕣 发布时间:&nbsp;</b> 2025-12-28<br>
<b>🧑‍💻 作&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;者:&nbsp;</b>&nbsp;&nbsp;AI & Liangxin<br>
<b>📞 联系方式:&nbsp;</b> 电话(同微信)：13700228563<br>
  <p style='font-size:14px; font-weight:bold; color:yellow;text-align:left;'>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本款人体时钟最早的创意来自日本人，原名：Hone Hone Clock，为Adobe Flash格式，后缀为swf，由于随着IE浏览器的退出，Flash技术在2020年底已经正式淘汰，目前几乎所有浏览器已经不支持网页运行Flash程序，原有的<a href="http://blog.itmyhome.com/hone_hone_clock/" target="_blank">演示地址</a>已经无法运行，<a href="https://github.com/itmyhome2013/hone_hone_clock">Github</a> 另有JS版本，本质还是内嵌swf文件，浏览器无法运行。<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本人基于原有的Flash文件以及图片资源，借用AI工具使用Python语言进行重构，仅为喜好。界面美观性效果较差，图片边缘有锯齿以及白边，如果有PS高手建议提供更多的趣味主题（比如比基尼人体艺术美女）。<br>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;人体时钟是一款基于PyQt6图形框架开发的创意桌面时钟应用，通过拟人化的人体造型和流畅的动画效果，将抽象的时间概念转化为直观生动的视觉体验。软件采用现代化的透明窗口设计，完美融入用户桌面环境，兼具实用性与趣味性。</p><br>
<b>主要特性:</b>
<ul style='font-size:14px; font-weight:bold;;text-align:left;'>
<li>🤟🏻 透明窗口，融入桌面环境</li>
<li>💗 生动的人体造型时间显示</li>
<li>🌈 丰富的背景颜色设置，支持全透明，预设颜色、自定义颜色、自定义透明度</li>
<li>🎨 支持主题切换（默认、黑色、白色、蓝色、红色）</li>
<li>🖱️ 鼠标缩放调整窗口大小（10%~200%）</li>
<li>📌 始终置顶选项</li>
<li>👁️ 支持分隔符是否闪烁设置</li>
<li>🖥️ 分屏适配</li>
<li>🌙 Windows深色主题兼容</li>
</ul>
<span style='position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); font-size:14px; font-weight:bold; color:#888;text-align:center;'>© 2025 AI & Liangxin. 永久免费</span><br><br>
        """
        
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("关于人体时钟")
        
        # 设置窗口标志确保关闭按钮可用
        dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint)
        
        # 创建标签和布局
        label = QLabel(about_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        dialog.setLayout(layout)
        
        # 设置样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgba(50, 50, 50, 255);
                color: white;
                border: 1px solid #777;
                border-radius: 8px;
                font-family: Microsoft YaHei, sans-serif;
                min-width: 500px;
            }
            QDialog QLabel {
                color: white;
                font-size: 14px;
                font-family: Microsoft YaHei, sans-serif;
                line-height: 1.6;
            }
        """)
        
        # 设置为模态对话框
        dialog.setModal(True)
        
        # 显示对话框
        dialog.exec()

class ClockDigit:
    def __init__(self, clock):
        self.clock = clock
        self.current_number = -1
        self.current_frame = 0
        self.stop_at = -1
        self.is_playing = False
        self.frame_timer = 0.0  # 用于控制帧切换的计时器
    
    def set_number(self, number):
        # 添加边界检查，确保数字始终在0-10范围内（10为分隔符）
        number = max(0, min(10, number))
        
        if self.current_number != number:
            self.current_number = number
            ani_data = self.clock.ani_data[number]
            self.stop_at = ani_data["frame_to"]
            self.current_frame = ani_data["frame_from"]
            self.is_playing = True
            self.frame_timer = 0.0
    
    def update_frame(self):
        # 对于分隔符，无论是否在播放，都要更新动画
        if self.current_number == 10:
            # 获取分隔符的总帧数
            ani_data = self.clock.ani_data[self.current_number]
            frame_count = ani_data["frame_to"] - ani_data["frame_from"] + 1
            
            
            total_duration = 1.0 / self.clock.animation_speed
            

            frame_duration = total_duration / frame_count
            

            self.frame_timer += 1.0 / 60.0
            

            if self.frame_timer >= frame_duration:
                self.current_frame += 1
                self.frame_timer = 0.0  # 重置计时器
                
    
                if self.current_frame >= self.stop_at:
                    if self.clock.colon_blinking:
            
                        ani_data = self.clock.ani_data[self.current_number]
                        self.current_frame = ani_data["frame_from"]
                    else:

                        self.current_frame = self.stop_at
        elif self.is_playing:
            # 获取当前数字的总帧数
            ani_data = self.clock.ani_data[self.current_number]
            frame_count = ani_data["frame_to"] - ani_data["frame_from"] + 1
            
            # 计算每个完整序列的总时长
            # 使用全局动画速度，确保所有数字动画时长一致
            total_duration = 1.0 / self.clock.animation_speed
            
            # 计算每个帧应该播放的时间（秒）
            frame_duration = total_duration / frame_count
            
            # 基于60fps更新计时器
            self.frame_timer += 1.0 / 60.0
            
            # 检查是否应该切换到下一帧
            if self.frame_timer >= frame_duration:
                self.current_frame += 1
                self.frame_timer = 0.0  # 重置计时器
                
                # 检查是否到达结束帧
                if self.current_frame > self.stop_at:
                    self.current_frame = self.stop_at
                    self.is_playing = False
    
    def draw(self, painter, x, y):
        # 获取当前数字类型
        digit_type = "colon" if self.current_number == 10 else str(self.current_number)
        
        pixmap = self.clock.get_frame_image(self.current_frame)
        if pixmap:
            # 根据当前缩放因子缩放pixmap
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * self.clock.scale_factor),
                int(pixmap.height() * self.clock.scale_factor),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            
            # 计算位置（确保所有元素水平居中，垂直基于底部对齐）
            draw_x = int(x - scaled_pixmap.width() // 2)
            # 统一使用底部对齐，确保所有元素在同一水平线上
            # y参数是基准线位置，所有元素的底部都对齐到这条线
            draw_y = int(y - scaled_pixmap.height())
            
            painter.drawPixmap(draw_x, draw_y, scaled_pixmap)

if __name__ == '__main__':
    # 支持高分屏缩放
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    # 设置应用程序不在最后一个窗口关闭时退出
    app.setQuitOnLastWindowClosed(False)
    clock = HoneHoneClock()
    clock.show()
    sys.exit(app.exec())
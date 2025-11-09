import sys
import json
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QListWidget, QListWidgetItem, QPushButton, QLabel,
                              QTextEdit, QHBoxLayout, QFileDialog, QMessageBox,
                              QSystemTrayIcon, QMenu, QLineEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard, QIcon, QFont, QAction

class ClipboardHistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("老黄剪贴板自动手机工具")
        self.setMinimumSize(1200, 700)  # 恢复之前的窗口大小
        
        # 设置应用图标
        self.app_icon = QIcon("icon.png")
        self.setWindowIcon(self.app_icon)
        
        # 初始化监听状态为开启
        self.monitoring_enabled = True
        
        # 设置存储路径为当前目录
        self.storage_path = Path("clipboard_history.json")
        
        # 设置主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(5)  # 减小布局间距
        main_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        
        # 左侧布局 - 列表和按钮
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(2)  # 减小控件间距
        left_layout.setContentsMargins(2, 2, 2, 2)  # 减小边距到最小
        
        # 创建状态和控制面板
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索历史记录...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        self.search_box.textChanged.connect(self.filter_history)
        control_layout.addWidget(self.search_box)
        
        # 创建监听开关按钮，默认为开启状态
        self.monitor_button = QPushButton("关闭监听")
        self.monitor_button.setCheckable(True)
        self.monitor_button.setChecked(True)  # 默认选中
        self.monitor_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked:hover {
                background-color: #45a049;
            }
        """)
        self.monitor_button.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.monitor_button)
        
        # 添加状态标签，默认显示监听状态
        self.status_label = QLabel("当前状态: 正在监听")
        self.status_label.setStyleSheet("color: #4CAF50;")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        left_layout.addWidget(control_panel)
        
        # 创建历史记录标签和列表的容器
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setSpacing(2)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建历史记录标签
        history_label = QLabel("历史记录:")
        history_label.setStyleSheet("QLabel { font-weight: bold; }")
        list_layout.addWidget(history_label)
        
        # 创建列表控件
        self.history_list = QListWidget()
        self.history_list.setFont(QFont("Microsoft YaHei", 10))
        self.history_list.currentItemChanged.connect(self.show_preview)
        self.history_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_list.setWordWrap(True)
        self.history_list.setSpacing(2)  # 添加项目间距
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                background-color: white;
                padding: 1px;  /* 减小列表内边距 */
                outline: none;  /* 移除整个列表的焦点边框 */
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                margin-bottom: 1px;
                background-color: #fafafa;
                border-radius: 3px;
                min-height: 60px;
                outline: none;  /* 移除列表项的焦点边框 */
            }
            QListWidget::item:selected {
                background-color: #e8f5e9;
                color: black;
                border: 1px solid #4CAF50;
            }
            QListWidget::item:focus {
                outline: none;  /* 确保焦点时也不显示边框 */
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        list_layout.addWidget(self.history_list)
        left_layout.addWidget(list_container)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)  # 保持按钮间距
        button_layout.setContentsMargins(0, 0, 0, 0)  # 移除按钮布局边距
        
        # 创建按钮并设置样式
        button_style = """
            QPushButton {
                padding: 4px 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_history)
        clear_button.setStyleSheet(button_style)
        button_layout.addWidget(clear_button)
        
        copy_button = QPushButton("复制")
        copy_button.clicked.connect(self.copy_selected)
        copy_button.setStyleSheet(button_style)
        button_layout.addWidget(copy_button)
        
        export_button = QPushButton("导出")
        export_button.clicked.connect(self.export_history)
        export_button.setStyleSheet(button_style)
        button_layout.addWidget(export_button)
        
        button_layout.addStretch()  # 添加弹性空间，使按钮靠左对齐
        
        left_layout.addLayout(button_layout)
        
        # 将左侧面板添加到主布局
        main_layout.addWidget(left_panel, 3)  # 增加左侧比例为3
        
        # 右侧布局 - 预览区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(2)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建预览标签
        preview_label = QLabel("内容预览:")
        preview_label.setStyleSheet("QLabel { font-weight: bold; }")
        right_layout.addWidget(preview_label)
        
        # 创建预览文本框
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Microsoft YaHei", 10))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                background-color: white;
                padding: 8px;
            }
        """)
        right_layout.addWidget(self.preview_text)
        
        # 将右侧面板添加到主布局
        main_layout.addWidget(right_panel, 2)  # 减小右侧比例为2
        
        # 初始化剪贴板监视器
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        
        # 加载历史记录
        self.load_history()
        
        # 设置定时保存
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_history)
        self.save_timer.start(30000)  # 每30秒保存一次
        
        # 设置系统托盘
        self.setup_system_tray()
    
    def setup_system_tray(self):
        # 创建系统托盘图标并使用相同的图标
        self.tray_icon = QSystemTrayIcon(self.app_icon, self)
        self.tray_icon.setToolTip("老黄剪贴板采集小工具")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 添加显示/隐藏动作
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        # 添加开关监听动作，默认显示关闭监听
        self.toggle_action = QAction("关闭监听", self)
        self.toggle_action.triggered.connect(self.monitor_button.click)
        tray_menu.addAction(self.toggle_action)
        
        # 添加分隔符
        tray_menu.addSeparator()
        
        # 添加退出动作
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 连接托盘图标的点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
    
    def toggle_monitoring(self):
        self.monitoring_enabled = self.monitor_button.isChecked()
        if self.monitoring_enabled:
            self.monitor_button.setText("关闭监听")
            self.status_label.setText("当前状态: 正在监听")
            self.status_label.setStyleSheet("color: #4CAF50;")
            self.toggle_action.setText("关闭监听")
        else:
            self.monitor_button.setText("开启监听")
            self.status_label.setText("当前状态: 未监听")
            self.status_label.setStyleSheet("color: #666;")
            self.toggle_action.setText("开启监听")
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_history()
            event.accept()
        else:
            event.ignore()
            self.hide()
    
    def on_clipboard_change(self):
        if not self.monitoring_enabled:
            return
            
        mime_data = self.clipboard.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if text.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # 只在列表预览中移除换行符
                preview_text = ' '.join(text.split())
                if len(preview_text) > 300:
                    preview_text = preview_text[:300] + "..."
                
                # 格式化显示，时间戳和内容分两行显示
                display_text = f"{timestamp}\n{preview_text}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, {
                    'timestamp': timestamp,
                    'text': text  # 保存原始文本
                })
                self.history_list.insertItem(0, item)
                self.history_list.setCurrentItem(item)
                self.save_history()
    
    def show_preview(self, current, previous):
        if current:
            data = current.data(Qt.UserRole)
            # 在预览区域显示完整的原始文本，保留换行符
            self.preview_text.setText(data['text'])
    
    def load_history(self):
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for entry in reversed(history):
                        # 只在列表预览中移除换行符
                        preview_text = ' '.join(entry['text'].split())
                        if len(preview_text) > 300:
                            preview_text = preview_text[:300] + "..."
                        # 格式化显示，时间戳和内容分两行显示
                        display_text = f"{entry['timestamp']}\n{preview_text}"
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.UserRole, {
                            'timestamp': entry['timestamp'],
                            'text': entry['text']  # 保存原始文本
                        })
                        self.history_list.addItem(item)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    
    def save_history(self):
        try:
            history = []
            for i in range(self.history_list.count()):
                item = self.history_list.item(i)
                data = item.data(Qt.UserRole)
                history.append(data)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_list.clear()
            self.preview_text.clear()
            self.save_history()
            QMessageBox.information(self, "提示", "历史记录已清空！")
    
    def copy_selected(self):
        current_item = self.history_list.currentItem()
        if current_item:
            data = current_item.data(Qt.UserRole)
            self.clipboard.setText(data['text'])
    
    def export_history(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出历史记录",
                str(Path.home() / "clipboard_history.txt"),
                "Text Files (*.txt)"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(self.history_list.count()):
                        item = self.history_list.item(i)
                        data = item.data(Qt.UserRole)
                        f.write(f"{data['text']}\n\n")
                QMessageBox.information(self, "导出成功", "历史记录已成功导出！")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出历史记录失败: {str(e)}")
    
    def filter_history(self, search_text):
        """根据搜索文本过滤历史记录"""
        search_text = search_text.lower()
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            data = item.data(Qt.UserRole)
            text_content = data['text'].lower()
            timestamp = data['timestamp'].lower()
            
            # 在时间戳和内容中搜索
            item.setHidden(search_text not in text_content and search_text not in timestamp)

def main():
    app = QApplication(sys.argv)
    window = ClipboardHistoryWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

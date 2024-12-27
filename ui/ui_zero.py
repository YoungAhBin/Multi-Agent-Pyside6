import sys

from PySide6 import  QtGui,QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot

from MyPySide6.Media_player import MediaPlayerWidget
from MyPySide6.reply.swarm_runner import BackendThread
from agents.triage_agent import triage_agent  # 确保 triage_agent 是对象

import os
import openai

# 设置 OpenAI API 密钥
openai.api_key = os.environ.get("OPENAI_API_KEY")

class MyWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("QFrame")
        self.resize(1000, 600)
        self.setup_ui()
        self.triage_agent = triage_agent
        self.backend_thread = None

    def setup_ui(self) -> None:
        """设置界面"""

        """左侧文件管理区界面"""
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.resize(200, 600)
        scroll_area.move(0, 0)

        #设置滚动区域为标签区域的父控件
        label_area = QtWidgets.QWidget(scroll_area)

        #设置标签区域为标签的父控件
        label_01 = QtWidgets.QLabel("文件名01", label_area)
        label_02 = QtWidgets.QLabel("文件名02", label_area)
        label_03 = QtWidgets.QLabel("文件名03", label_area)
        label_04 = QtWidgets.QLabel("文件名04", label_area)

        # 创建布局管理器对象，创建时指定布局方向为垂直从上至下
        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        # 将布局管理器添加给标签区域，用于管理标签区域的控件
        label_area.setLayout(layout)
        # 将控件添加到布局管理器中，就像setWidget，不添加，就不纳入布局管理器的管理
        layout.addWidget(label_01)
        layout.addWidget(label_02)
        layout.addWidget(label_03)
        layout.addWidget(label_04)
        
        # 添加为滚动区域的子控件，并不能作为滚动区域的滚不动内容展示。只有用下列这行代码将控件添加为滚动区域的视图控件，才会变为滚动展示的内容,并且setWidget只能添加一个控件作为视图控件，所以多个标签要放在label_area中
        scroll_area.setWidget(label_area)

        # 设置视图控件的对齐方式，这是滚动区域用于管理自己的视图控件的方法
        scroll_area.setAlignment(
            Qt.AlignLeft
        )  # 设置为水平居中
        
        """中间对话界面"""
        self.frame = QtWidgets.QFrame(self)
        self.frame.setStyleSheet("background-color: white;")
        self.frame.resize(500, 600)
        self.frame.move(200, 0)
        # 设置风格与线宽
        self.frame.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel | QtWidgets.QFrame.Shadow.Sunken)
        self.frame.setLineWidth(3)

        # 创建对话窗口
        self.text_browser = QtWidgets.QTextBrowser(self.frame)
        #text_browser.setText(self.text)
        self.text_browser.resize(500, 400)
        self.text_browser.move(0, 0)
        self.text_browser.setStyleSheet("""
        QTextBrowser {
            border: none;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            border-left: 1px solid rgba(0, 0, 0, 0.1);
            border-right: 1px solid rgba(0, 0, 0, 0.1);
            border-bottom: 1px solid rgba(0, 0, 0, 0.2);
        }
        """)
        
        # pte = QtWidgets.QPlainTextEdit(self)  # 创建
        self.pte = QtWidgets.QPlainTextEdit(self.frame)
        self.pte.resize(500, 200)
        self.pte.move(0, 400)
        self.pte.setStyleSheet("background-color: white; font-size: 13px; line-height: 1.0; letter-spacing: 1.5px;")

        self.button = QtWidgets.QPushButton()
        self.button.setParent(self.frame)  # 创建时父对象为None,可用setParent方法指定
        self.button.setText("发送")  # 设置按钮上的文字
        self.button.clicked.connect(self.send_message)
        # 定位按钮到右下角
        self.button.resize(100, 40)  # 设置按钮大小
        self.button.move(self.frame.width() - self.button.width() - 10, self.frame.height() - self.button.height() - 10)

        """右侧多媒体播放与功能界面"""
        # 创建并嵌入MediaPlayerWidget
        self.media_player = MediaPlayerWidget(self)
        self.media_player.resize(300, 207)
        self.media_player.move(700, 0)

        ribbon = QtWidgets.QFrame(self)
        ribbon.resize(300, 393)
        ribbon.move(700, 207)
        ribbon.setStyleSheet("background-color: #FAFAFA;")
        # 设置风格与线宽
        ribbon.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel | QtWidgets.QFrame.Shadow.Sunken)
        ribbon.setLineWidth(3)

    def send_message(self):
        user_input = self.pte.toPlainText().strip()
        if not user_input:
            return

        # 显示用户输入到 QTextBrowser      
        self.text_browser.append(
            f'<div style="margin-bottom: 10px; font-size: 13px; letter-spacing: 1.5px; line-height: 1.0;">'
            f'<span style="color: green; font-weight: bold;">用户:</span><br>{user_input}<br></div>'
        )

        # 清空输入框
        self.pte.clear()

        # 如果有现存的线程在运行，先终止它
        if self.backend_thread and self.backend_thread.isRunning():
            self.backend_thread.terminate()
            self.backend_thread.wait()

        # 创建并启动新的后台线程
        self.backend_thread = BackendThread(
            user_input=user_input,
            starting_agent=self.triage_agent,
            context_variables=None,  # 根据需要传递上下文变量
            stream=True,            # 根据需要设置是否流式
            debug=False              # 根据需要设置调试模式
        )

        # 连接信号
        self.backend_thread.response_chunk.connect(self.update_text_browser)

        # 启动线程
        self.backend_thread.start()

    @Slot(str)
    def update_text_browser(self, text):
        self.text_browser.insertHtml(f'<div style="margin-bottom: 10px; font-size: 13px; letter-spacing: 1.5px; line-height: 1.0;">{text}</div>')

    def closeEvent(self, event):
        # 确保线程在关闭时正确终止
        if self.backend_thread and self.backend_thread.isRunning():
            self.backend_thread.terminate()
            self.backend_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())

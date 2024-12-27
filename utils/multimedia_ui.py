# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QSlider, QFileDialog, QLabel, QStyle)
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget


class MediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化播放器和音频输出
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # 视频显示组件
        self.video_widget = QVideoWidget()

        # 控制按钮
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pause_button.clicked.connect(self.pause)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop)

        self.open_button = QPushButton("打开")
        self.open_button.clicked.connect(self.open_file)

        # 音量滑块
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        self.volume_slider.valueChanged.connect(self.set_volume)

        # 布局设置
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(QLabel("音量"))
        control_layout.addWidget(self.volume_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

        # 设置视频输出
        self.player.setVideoOutput(self.video_widget)

        # 连接播放器信号
        self.player.playbackStateChanged.connect(self.update_buttons)
        self.player.errorOccurred.connect(self.handle_error)

        self.update_buttons(self.player.playbackState())

    @Slot()
    def open_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setMimeTypeFilters(self.get_supported_mime_types())
        if file_dialog.exec() == QFileDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            self.player.setSource(url)
            self.player.play()

    def get_supported_mime_types(self):
        # 获取支持的 MIME 类型
        mime_types = []
        for f in QMediaPlayer.supportedMimeTypes():
            mime_types.append(f)
        return mime_types

    @Slot()
    def play(self):
        self.player.play()

    @Slot()
    def pause(self):
        self.player.pause()

    @Slot()
    def stop(self):
        self.player.stop()

    @Slot(int)
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    @Slot()
    def update_buttons(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        elif state == QMediaPlayer.PausedState:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    @Slot()
    def handle_error(self, error, error_string):
        if error != QMediaPlayer.NoError:
            print(f"播放器错误: {error_string}")

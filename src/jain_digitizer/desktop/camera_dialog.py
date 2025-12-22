import os
import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QLabel, QWidget)
from PySide6.QtMultimedia import (QMediaDevices, QCamera, QImageCapture, 
                                QMediaCaptureSession, QVideoFrame)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from jain_digitizer.common.logger_setup import logger

class CameraDialog(QDialog):
    image_captured = Signal(str) # Emits the path of the saved image

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capture from Camera")
        self.resize(800, 600)
        
        self.capture_dir = os.path.join(os.getcwd(), "captures")
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir)

        self.setup_ui()
        self.init_camera()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Camera Selection
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Select Camera:"))
        self.camera_selector = QComboBox()
        self.camera_selector.currentIndexChanged.connect(self.change_camera)
        top_layout.addWidget(self.camera_selector, 1)
        layout.addLayout(top_layout)

        # Video Preview
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 480)
        layout.addWidget(self.video_widget)

        # Controls
        controls_layout = QHBoxLayout()
        self.btn_capture = QPushButton("📸 Capture Photo")
        self.btn_capture.setFixedHeight(40)
        self.btn_capture.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_capture.clicked.connect(self.take_photo)
        
        self.btn_done = QPushButton("Done")
        self.btn_done.setFixedHeight(40)
        self.btn_done.clicked.connect(self.accept)
        
        controls_layout.addWidget(self.btn_capture, 2)
        controls_layout.addWidget(self.btn_done, 1)
        layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def init_camera(self):
        self.session = QMediaCaptureSession()
        self.image_capture = QImageCapture()
        self.session.setImageCapture(self.image_capture)
        self.session.setVideoOutput(self.video_widget)

        self.image_capture.imageSaved.connect(self.on_image_saved)
        self.image_capture.errorOccurred.connect(self.on_capture_error)

        self.update_camera_list()

    def update_camera_list(self):
        self.camera_selector.clear()
        self.cameras = QMediaDevices.videoInputs()
        for i, camera in enumerate(self.cameras):
            self.camera_selector.addItem(camera.description(), camera)
        
        if self.cameras:
            self.camera_selector.setCurrentIndex(0)

    def change_camera(self, index):
        if index < 0 or index >= len(self.cameras):
            return

        camera_device = self.camera_selector.itemData(index)
        
        if hasattr(self, 'camera'):
            self.camera.stop()
        
        self.camera = QCamera(camera_device)
        self.camera.errorOccurred.connect(self.on_camera_error)
        self.session.setCamera(self.camera)
        self.camera.start()
        logger.info(f"Switched to camera: {camera_device.description()}")
        self.status_label.setText(f"Using: {camera_device.description()}")

    def on_camera_error(self, error, error_string):
        logger.error(f"Camera error: {error_string}")
        import platform
        system = platform.system()
        
        if "AccessToCameraThreshold" in error_string or "not granted" in error_string.lower() or "denied" in error_string.lower():
            if system == "Darwin":
                msg = "Error: Camera access denied. Check System Settings > Privacy & Security > Camera"
            elif system == "Windows":
                msg = "Error: Camera access denied. Check Windows Settings > Privacy & Security > Camera"
            elif system == "Linux":
                msg = "Error: Camera access denied. Check if your user is in the 'video' group or if another app is using it."
            else:
                msg = "Error: Camera access denied. Please check your system's privacy settings."
            self.status_label.setText(msg)
        else:
            self.status_label.setText(f"Camera Error: {error_string}")

    def take_photo(self):
        if not hasattr(self, 'camera') or not self.camera.isActive():
            logger.error("Camera not active")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(self.capture_dir, filename)
        
        # QImageCapture.capture() doesn't take a path anymore in Qt6.6+ for some versions?
        # Actually it takes a path or provides a ID.
        self.image_capture.captureToFile(filepath)
        self.status_label.setText("Capturing...")
        self.btn_capture.setEnabled(False)

    def on_image_saved(self, id, fileName):
        logger.info(f"Image saved to: {fileName}")
        self.image_captured.emit(fileName)
        self.status_label.setText(f"Captured: {os.path.basename(fileName)}")
        self.btn_capture.setEnabled(True)

    def on_capture_error(self, id, error, errorMsg):
        logger.error(f"Capture error: {errorMsg}")
        self.status_label.setText(f"Error: {errorMsg}")
        self.btn_capture.setEnabled(True)

    def closeEvent(self, event):
        if hasattr(self, 'camera'):
            self.camera.stop()
        super().closeEvent(event)

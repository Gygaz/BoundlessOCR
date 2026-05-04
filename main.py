import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QThread, Slot
from ocr.processor import Worker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Text Converter")
        self.setMinimumSize(400, 300)
        
        container = QWidget()
        self.setCentralWidget(container)
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.title_label = QLabel("OCR Scanner")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.StyledPanel)
        frame_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Waiting for file...")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        self.file_label.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.file_label)
        self.layout.addWidget(self.status_frame)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.layout.addWidget(self.progress)

        self.load_btn = QPushButton("Select PDF")
        self.load_btn.clicked.connect(self.load_pdf)
        
        self.start_btn = QPushButton("Process")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_process)
        self.start_btn.setStyleSheet("background-color: #5c110c; color: white; font-weight: bold; height: 30px;")

        self.layout.addWidget(self.load_btn)
        self.layout.addWidget(self.start_btn)
        
        self.current_file = [None]

    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.current_file[0] = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.start_btn.setEnabled(True)

    def start_process(self):
        # Setup Thread and Worker
        self.thread = QThread()
        self.worker = Worker(self.current_file)
        self.worker.moveToThread(self.thread)

        # Signals
        self.thread.started.connect(self.worker.process_pdf)
        self.worker.status_message.connect(self.status_label.setText)
        self.worker.progress_update.connect(self.progress.setValue)
        
        # Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.on_finished)

        # UI State
        self.start_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.thread.start()

    def on_finished(self):
        self.load_btn.setEnabled(True)
        QMessageBox.information(self, "Success", "PDF Processed Successfully!")

app= QApplication(sys.argv)
window= MainWindow()
window.show()
sys.exit(app.exec())
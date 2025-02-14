from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QUrl
import sys
import os
from capture_traffic1 import *
from nids_form import *
from gemini_rag_for_saving_sessions import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("IncidenceResponseAI")
        self.setGeometry(100, 100, 1200, 800)

        # Create a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # QWebEngineView to render the HTML
        self.webview = QWebEngineView()
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        layout.addWidget(self.webview)
        
        self.webview.setUrl(QUrl("http://127.0.0.1:5006"))

        # Load the HTML file
        html_path = os.path.abspath(r"C:\Users\DELL\VS_Code_Files\thesis\ai.html")
        self.webview.setUrl(QUrl.fromLocalFile(html_path))
        
        css_path = os.path.abspath(r"C:\Users\DELL\VS_Code_Files\thesis\index.css")
        if not os.path.exists(css_path):
            print("Warning: 'index.css' file is missing. Ensure your HTML references it correctly.")
    
    def show_error_message(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()

if __name__ == "__main__":
    # Check if the required files exist
    if not os.path.exists(r"C:\Users\DELL\VS_Code_Files\thesis\ai.html"):
        print("Error: 'index.html' file is missing.")
        sys.exit(1)
    if not os.path.exists(r"C:\Users\DELL\VS_Code_Files\thesis\index.css"):
        print("Warning: 'index.css' file is missing. Ensure your HTML references it correctly.")
    
    start_nids_server()
    
    start_traffic_monitoring()
    
    start_rag_server()

    # Run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

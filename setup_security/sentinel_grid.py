import sys, os, subprocess, threading, cv2, time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

# --- 1. THE SIMPLE BOOT SCREEN ---
class IntroOverlay(QWidget):
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.count = 0  # CRITICAL: Initialize before anything else
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_intro)
        self.timer.start(100)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QColor(0, 255, 0))
        p.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        dots = "." * (self.count % 4)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"ENABLING SECURITY KERNEL{dots}")

    def update_intro(self):
        self.count += 1
        if self.count > 15: # Very fast 1.5s boot
            self.timer.stop()
            self.finished.emit()
            self.close()
        self.update()

# --- 2. THE 3D GLOBE ---
class SimpleGlobe(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.rot = 0
        self.timer = QTimer(self); self.timer.timeout.connect(self.update); self.timer.start(20)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glLoadIdentity()
        glTranslatef(0, 0, -10); glRotatef(self.rot, 0, 1, 0); glRotatef(20, 1, 0, 0)
        self.rot += 1
        glColor4f(0, 1, 0, 0.4)
        q = gluNewQuadric(); gluQuadricDrawStyle(q, GLU_LINE)
        gluSphere(q, 4, 15, 15)

# --- 3. THE MAIN OS WITH SHUTDOWN PROTOCOL ---
class SentinelOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background:#000; color:#0f0; font-family:Consolas;")
        
        self.init_ui()
        # Start the "Dead Man's Switch" Security Thread
        threading.Thread(target=self.security_monitor, daemon=True).start()

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        left = QVBoxLayout()
        self.globe = SimpleGlobe(self)
        self.status = QLabel(">> SECURITY: MONITORING OPERATOR...")
        self.status.setStyleSheet("font-size: 18px; color: #0f0;")
        left.addWidget(self.globe, 5); left.addWidget(self.status, 1)
        layout.addLayout(left, 1)
        
        right = QVBoxLayout()
        self.term = QTextEdit(); self.term.setReadOnly(True)
        self.term.setStyleSheet("border: 1px solid #0f0; background:#000; color:#0f0;")
        self.cmd = QLineEdit(); self.cmd.setPlaceholderText("ROOT@SENTINEL:~#")
        self.cmd.setStyleSheet("border: 1px solid #0f0; padding:10px; color:#0f0;")
        self.cmd.returnPressed.connect(self.run_cmd)
        
        right.addWidget(QLabel("--- SENTINEL SECURITY KERNEL ---"))
        right.addWidget(self.term, 5); right.addWidget(self.cmd, 1)
        layout.addLayout(right, 1)

    def run_cmd(self):
        txt = self.cmd.text(); self.cmd.clear()
        self.term.append(f"<font color='white'># {txt}</font>")
        if txt.lower() == "safe-exit": os._exit(0) # Standard exit for when you are done

    def security_monitor(self):
        cap = cv2.VideoCapture(0)
        # Use the standard Haar Cascade for faces (very fast)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        missing_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                missing_frames += 1
                self.status.setText(f">> ALERT: OPERATOR ABSENT ({missing_frames})")
                self.status.setStyleSheet("color: red;")
                
                # If operator is gone for ~3 seconds (6 frames at 0.5s intervals)
                if missing_frames > 6:
                    self.trigger_shutdown()
                    break
            else:
                missing_frames = 0
                self.status.setText(">> SECURITY: OPERATOR VERIFIED")
                self.status.setStyleSheet("color: #0f0;")
            
            time.sleep(0.5)

    def trigger_shutdown(self):
        # 1. Close the program immediately
        QMetaObject.invokeMethod(self.term, "append", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "<font color='red'>CRITICAL: TRIGGERING EMERGENCY SHUTDOWN!</font>"))
        time.sleep(1)
        
        # 2. Force Windows Shutdown
        # /s = shutdown, /f = force close apps, /t 0 = zero second delay
        os.system("shutdown /s /f /t 0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    boot = IntroOverlay()
    boot.finished.connect(lambda: SentinelOS().show())
    sys.exit(app.exec())
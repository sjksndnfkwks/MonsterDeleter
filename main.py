import sys
import os
import winreg
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal, QUrl, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter, QColor, QTransform, QImage, QPainterPath, QCursor, QPen
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from app_utils import find_windowless_python, validate_target

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

SPRITE_DIR = get_resource_path("assets")
COLS = 5
ROWS = 3

def register_context_menu():
    try:
        exe_path = sys.executable
        if not getattr(sys, "frozen", False):
            exe_path = find_windowless_python(exe_path)
            script_path = os.path.abspath(__file__)
            command_str = f'"{exe_path}" "{script_path}" "%1"'
            icon_str = "shell32.dll,32"
        else:
            command_str = f'"{exe_path}" "%1"'
            icon_str = f'"{exe_path}",0'
            
        key_path = r"Software\Classes\*\shell\SummonMonster"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "召唤大将怪兽摧毁")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_str)
        winreg.CloseKey(key)
        
        command_key_path = key_path + r"\command"
        command_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key_path)
        winreg.SetValue(command_key, "", winreg.REG_SZ, command_str)
        winreg.CloseKey(command_key)
        return True, None
    except Exception as e:
        print(f"Error registering menu: {e}")
        return False, str(e)

class SpriteAnimator(QLabel):
    animationFinished = pyqtSignal()
    frameChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frames = []
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.loop = True
        self.flip_horizontal = False
        self.is_playing = False

    def load_spritesheet(self, filepath, cols=COLS, rows=ROWS, target_height=250, frame_indices=None):
        self.stop()
        self.frames = []
        self.current_frame = 0

        if cols <= 0 or rows <= 0 or target_height <= 0:
            print("Error: Invalid spritesheet dimensions")
            return False

        transparent_path = filepath.replace(".png", "_transparent.png")
        if os.path.exists(transparent_path):
            filepath = transparent_path
            
        if not os.path.exists(filepath):
            print(f"Error: Sprite not found at {filepath}")
            return False
            
        image = QImage(filepath)
        if image.isNull():
            print(f"Error: Failed to load image {filepath}")
            return False
        if image.width() < cols or image.height() < rows:
            print(f"Error: Spritesheet is too small for a {cols}x{rows} grid: {filepath}")
            return False
            
        pixmap = QPixmap.fromImage(image)
        
        frame_w = pixmap.width() // cols
        frame_h = pixmap.height() // rows
        
        for r in range(rows):
            for c in range(cols):
                frame = pixmap.copy(c * frame_w, r * frame_h, frame_w, frame_h)
                frame = frame.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
                self.frames.append(frame)
                
        if frame_indices is not None:
            self.frames = [self.frames[i] for i in frame_indices if 0 <= i < len(self.frames)]
                
        if self.frames:
            self.resize(self.frames[0].size())
        return bool(self.frames)

    def set_flip(self, flip):
        self.flip_horizontal = flip
        self._update_frame()

    def play(self, fps=8, loop=True):
        if not self.frames or fps <= 0:
            self.stop()
            return False
        self.loop = loop
        self.current_frame = 0
        self.is_playing = True
        self.timer.start(1000 // fps)
        self._update_frame()
        return True

    def stop(self):
        self.timer.stop()
        self.is_playing = False

    def next_frame(self):
        if not self.frames:
            return
            
        self.current_frame += 1
        if self.current_frame >= len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.current_frame = len(self.frames) - 1
                self.stop()
                self._update_frame()
                self.frameChanged.emit(self.current_frame)
                self.animationFinished.emit()
                return
                
        self._update_frame()
        self.frameChanged.emit(self.current_frame)
        
    def _update_frame(self):
        if not self.frames:
            return
        frame = self.frames[self.current_frame]
        if self.flip_horizontal:
            transform = QTransform().scale(-1, 1)
            frame = frame.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(frame)


from PyQt6.QtGui import QPainterPath

class BubbleWidget(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 15) # Leave space at bottom for the tail
        self.lbl_text = QLabel(text)
        
        # Modern Sleek UI Design for text
        style = """
            QLabel {
                color: #1c1c1e; 
                padding: 15px 30px; 
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; 
                font-size: 20px; 
                font-weight: 600;
            }
        """
        self.lbl_text.setStyleSheet(style)
        
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_text)
        self.setLayout(layout)
        
        # Soft realistic modern shadow on the whole widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 240))
        
        rect = self.rect()
        
        # Bubble body
        path = QPainterPath()
        path.addRoundedRect(0, 0, float(rect.width()), float(rect.height() - 15), 20.0, 20.0)
        
        # Dialog Tail pointing to the monster (bottom middle)
        tail = QPainterPath()
        tail.moveTo(float(rect.width()) / 2 - 15, float(rect.height() - 15))
        tail.lineTo(float(rect.width()) / 2, float(rect.height()))
        tail.lineTo(float(rect.width()) / 2 + 15, float(rect.height() - 15))
        path.addPath(tail)
        
        painter.drawPath(path)

class ChoicesWidget(QWidget):
    choiceMade = pyqtSignal()
    cancelled = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        self.btn1 = QPushButton("确认移至回收站")
        self.btn2 = QPushButton("取消")
        
        # Modern Sleek UI Design
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 240); 
                color: #1c1c1e; 
                border: 1px solid #e5e5ea; 
                border-radius: 18px; 
                padding: 12px 25px; 
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; 
                font-size: 16px; 
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #007aff;
                color: #ffffff;
                border: 1px solid #007aff;
            }
            QPushButton:pressed {
                background-color: #005bb5;
                color: #ffffff;
            }
        """
        self.btn1.setStyleSheet(btn_style)
        self.btn2.setStyleSheet(btn_style)
        
        # Add soft shadows to buttons
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(15)
        shadow1.setOffset(0, 5)
        shadow1.setColor(QColor(0, 0, 0, 30))
        self.btn1.setGraphicsEffect(shadow1)

        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setOffset(0, 5)
        shadow2.setColor(QColor(0, 0, 0, 30))
        self.btn2.setGraphicsEffect(shadow2)
        
        self.btn1.clicked.connect(self.on_confirm)
        self.btn2.clicked.connect(self.on_cancel)
        
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        self.setLayout(layout)

    def on_confirm(self):
        self.hide()
        self.choiceMade.emit()

    def on_cancel(self):
        self.hide()
        self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.on_cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self.isVisible():
            self.cancelled.emit()
        event.accept()
        

class MonsterDeleter(QWidget):
    def __init__(self, target_file):
        super().__init__()
        self.target_file = os.path.abspath(os.fspath(target_file))
        self.target_pos = None
        self._bg_opacity = 0.0
        self.monster_sequence_started = False
        self.deletion_succeeded = False
        self.deletion_error = None
        self._closing = False
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        self.animator = SpriteAnimator(self)
        self.animator.hide()
        
        self.explosion_animator = SpriteAnimator(self)
        self.explosion_animator.hide()
        
        self.bubble = BubbleWidget(f"确认将此文件移至回收站吗？\n{self.target_file}")
        self.bubble.lbl_text.setWordWrap(True)
        self.bubble.lbl_text.setMaximumWidth(600)
        self.bubble.lbl_text.setToolTip(self.target_file)
        self.choices = ChoicesWidget()
        self.choices.cancelled.connect(self.cancel_operation)
        
        self.init_audio()
        
        # Always launch the sniper targeting UI for interactive aiming
        self.init_targeting_ui()

    @pyqtProperty(float)
    def bg_opacity(self):
        return self._bg_opacity
        
    @bg_opacity.setter
    def bg_opacity(self, value):
        self._bg_opacity = value
        self.update()

    def init_audio(self):
        # Background Music
        self.bgm_player = QMediaPlayer()
        self.bgm_audio = QAudioOutput()
        self.bgm_player.setAudioOutput(self.bgm_audio)
        bgm_path = get_resource_path(r"assets\音频\bgm(1).mp3")
        self.bgm_player.setSource(QUrl.fromLocalFile(bgm_path))
        self.bgm_audio.setVolume(0.5)
        self.bgm_player.mediaStatusChanged.connect(self.loop_bgm)
        
        # Sound Effects
        self.sfx_player = QMediaPlayer()
        self.sfx_audio = QAudioOutput()
        self.sfx_player.setAudioOutput(self.sfx_audio)
        sfx_path = get_resource_path(r"assets\音频\怪兽说话.mp3")
        self.sfx_player.setSource(QUrl.fromLocalFile(sfx_path))
        self.sfx_audio.setVolume(1.0)
        
        # Explosion Sound
        self.exp_player = QMediaPlayer()
        self.exp_audio = QAudioOutput()
        self.exp_player.setAudioOutput(self.exp_audio)
        exp_path = get_resource_path(r"assets\音频\爆炸.MP4")
        self.exp_player.setSource(QUrl.fromLocalFile(exp_path))
        self.exp_audio.setVolume(0.3)

    def loop_bgm(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.bgm_player.setPosition(0)
            self.bgm_player.play()

    def init_targeting_ui(self):
        # Create a custom red sniper cursor
        cursor_size = 40
        cursor_pixmap = QPixmap(cursor_size, cursor_size)
        cursor_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(cursor_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(255, 0, 0)) # Red color
        pen.setWidth(2)
        painter.setPen(pen)
        
        center = cursor_size // 2
        radius = 12
        # Draw outer circle
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        
        # Draw crosshairs
        painter.drawLine(center, 0, center, center - 4) # Top
        painter.drawLine(center, center + 4, center, cursor_size) # Bottom
        painter.drawLine(0, center, center - 4, center) # Left
        painter.drawLine(center + 4, center, cursor_size, center) # Right
        
        painter.end()
        
        self.setCursor(QCursor(cursor_pixmap, center, center))
        
        # Start fade in
        self.fade_in_anim = QPropertyAnimation(self, b"bg_opacity")
        self.fade_in_anim.setDuration(800)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(0.35) # Reduced opacity
        self.fade_in_anim.start()
        
    def paintEvent(self, event):
        if self._bg_opacity > 0.01:
            painter = QPainter(self)
            
            # Draw semi-transparent background image
            bg_image_path = ""
            for ext in [".png", ".jpg", ".jpeg"]:
                test_path = get_resource_path(rf"assets\选择界面\选择界面{ext}")
                if os.path.exists(test_path):
                    bg_image_path = test_path
                    break
                    
            if os.path.exists(bg_image_path):
                bg_image = QImage(bg_image_path)
                if not bg_image.isNull():
                    painter.setOpacity(self._bg_opacity) # Animated opacity
                    scaled_img = bg_image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    x = (self.width() - scaled_img.width()) // 2
                    y = (self.height() - scaled_img.height()) // 2
                    painter.drawImage(x, y, scaled_img)
            else:
                painter.setOpacity(self._bg_opacity)
                painter.fillRect(self.rect(), QColor(0, 0, 0, 160))
                
            # Scale text opacity relative to bg_opacity max (0.35)
            text_opacity = min(1.0, self._bg_opacity / 0.35)
            painter.setOpacity(text_opacity)
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(30)
            font.setBold(True)
            painter.setFont(font)
            target_name = os.path.basename(self.target_file)
            prompt = f"点击希望爆炸出现的位置\n目标文件：{target_name}\n按 Esc 取消"
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, prompt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_operation()
            event.accept()
            return
        super().keyPressEvent(event)

    def cancel_operation(self):
        self.close()

    def mousePressEvent(self, event):
        if not self.monster_sequence_started and event.button() == Qt.MouseButton.LeftButton:
            self.target_pos = event.pos()
            self.monster_sequence_started = True
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            self.fade_out_anim = QPropertyAnimation(self, b"bg_opacity")
            self.fade_out_anim.setDuration(500)
            self.fade_out_anim.setStartValue(self._bg_opacity)
            self.fade_out_anim.setEndValue(0.0)
            self.fade_out_anim.finished.connect(self.init_monster_sequence)
            self.fade_out_anim.start()

    def init_monster_sequence(self):
        self.start_phase1_walk()

    def start_phase1_walk(self):
        
        # Start playing BGM here
        self.bgm_player.play()
        
        if not self.load_animation(self.animator, "走路动效_spritesheet.png"):
            return
        
        start_x = -self.animator.width()
        start_y = self.target_pos.y() - self.animator.height() // 2 + 50 # Move pet down
        
        self.from_right = False
        self.animator.set_flip(False) 
            
        self.animator.move(start_x, start_y)
        self.animator.show()
        self.animator.play(fps=8, loop=True)
        
        self.move_anim = QPropertyAnimation(self.animator, b"pos")
        self.move_anim.setDuration(4500) # Slower walking speed
        
        # Move pet left so the finger hits the file exactly
        end_x = self.target_pos.x() - self.animator.width() - 30

        self.move_anim.setStartValue(QPoint(start_x, start_y))
        self.move_anim.setEndValue(QPoint(end_x, start_y))
        self.move_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.move_anim.finished.connect(self.start_phase2_point)
        self.move_anim.start()

    def start_phase2_point(self):
        # Play SFX once when pointing animation starts
        self.sfx_player.play()
        
        # Phase 2: Pointing (Play ONCE, frames 11-14 only)
        if not self.load_animation(self.animator, "指着文件_spritesheet.png", frame_indices=[11, 12, 13, 14]):
            return
        
        try:
            self.animator.animationFinished.disconnect()
        except TypeError:
            pass
            
        self.animator.animationFinished.connect(self.show_dialog)
        self.animator.play(fps=8, loop=False)

    def show_dialog(self):
        try:
            self.animator.animationFinished.disconnect()
        except TypeError:
            pass
            
        global_pos = self.mapToGlobal(self.animator.pos())
        
        bubble_x = global_pos.x() + (self.animator.width() // 2) - 80
        bubble_y = global_pos.y() - 60 # Moved bubble down
        self.bubble.move(bubble_x, bubble_y)
        self.bubble.show()

        choices_x = global_pos.x() + (self.animator.width() // 2) - 130
        choices_y = global_pos.y() + self.animator.height() - 20 # Moved choices down
        self.choices.move(choices_x, choices_y)
        
        try:
            self.choices.choiceMade.disconnect()
        except TypeError:
            pass
            
        self.choices.choiceMade.connect(self.start_phase3_kick)
        self.choices.show()

    def start_phase3_kick(self):
        self.bubble.hide()
        
        try:
            self.animator.animationFinished.disconnect()
            self.animator.frameChanged.disconnect()
        except TypeError:
            pass
            
        if not self.load_animation(self.animator, "踹文件动效_spritesheet.png"):
            return
        self.animator.animationFinished.connect(self.on_kick_finished)
        self.animator.frameChanged.connect(self.on_kick_frame)
        self.animator.play(fps=8, loop=False)

    def on_kick_frame(self, frame_idx):
        # Trigger explosion precisely on the 6th frame (index 5)
        if frame_idx == 5:
            self.trigger_explosion()

    def trigger_explosion(self):
        # Play explosion sound
        self.exp_player.play()
        
        # Slightly larger explosion (150 instead of 100)
        if not self.load_animation(self.explosion_animator, "爆炸_spritesheet.png", target_height=150):
            return
        
        # Center explosion slightly higher to cover the file icon properly
        exp_x = self.target_pos.x() - self.explosion_animator.width() // 2
        exp_y = self.target_pos.y() - self.explosion_animator.height() // 2 - 40
        self.explosion_animator.move(exp_x, exp_y)
        self.explosion_animator.show()
        
        try:
            self.explosion_animator.animationFinished.disconnect()
        except TypeError:
            pass
            
        self.explosion_animator.animationFinished.connect(self.explosion_animator.hide)
        self.explosion_animator.play(fps=8, loop=False)
        
        # We can trigger the file deletion here to perfectly sync with explosion
        self.deletion_succeeded, self.deletion_error = self.delete_target_file()

    def delete_target_file(self):
        try:
            from send2trash import send2trash
            if not os.path.isfile(self.target_file):
                return False, f"目标文件已不存在：\n{self.target_file}"
            send2trash(self.target_file)
            print(f"Moved to trash: {self.target_file}")
            return True, None
        except Exception as e:
            print(f"Error: {e}")
            return False, f"无法将文件移至回收站：\n{self.target_file}\n\n{e}"

    def on_kick_finished(self):
        try:
            self.animator.animationFinished.disconnect()
            self.animator.frameChanged.disconnect()
        except TypeError:
            pass
            
        if not self.deletion_succeeded:
            self.show_error_and_close(self.deletion_error or "文件删除失败。")
            return
        self.start_phase4_leo()

    def start_phase4_leo(self):
        if not self.load_animation(self.animator, "雷欧登场_spritesheet.png"):
            return
        self.animator.animationFinished.connect(self.start_phase5_fly)
        self.animator.play(fps=8, loop=False)

    def start_phase5_fly(self):
        try:
            self.animator.animationFinished.disconnect()
        except TypeError:
            pass
            
        if not self.load_animation(self.animator, "出场飞行动效_spritesheet.png"):
            return
        self.animator.play(fps=8, loop=True)
        
        self.move_anim2 = QPropertyAnimation(self.animator, b"pos")
        self.move_anim2.setDuration(2000)
        self.move_anim2.setStartValue(self.animator.pos())
        
        end_x = self.width() + 200
        end_y = self.animator.pos().y()
            
        self.move_anim2.setEndValue(QPoint(end_x, end_y))
        self.move_anim2.setEasingCurve(QEasingCurve.Type.InQuad)
        self.move_anim2.finished.connect(self.on_app_exit)
        self.move_anim2.start()

    def on_app_exit(self):
        self.close()

    def load_animation(self, animator, filename, **kwargs):
        path = os.path.join(SPRITE_DIR, filename)
        if animator.load_spritesheet(path, **kwargs):
            return True
        self.show_error_and_close(f"动画资源无法加载：\n{path}")
        return False

    def show_error_and_close(self, message):
        self.bgm_player.stop()
        self.sfx_player.stop()
        self.exp_player.stop()
        QMessageBox.critical(self, "大将怪兽", message)
        self.close()

    def closeEvent(self, event):
        if self._closing:
            event.accept()
            return
        self._closing = True
        self.animator.stop()
        self.explosion_animator.stop()
        self.bgm_player.stop()
        self.sfx_player.stop()
        self.exp_player.stop()
        self.bubble.close()
        self.choices.close()
        event.accept()
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    registered, registration_error = register_context_menu()

    target, target_error = validate_target(sys.argv[1] if len(sys.argv) >= 2 else None)
    if target is None:
        if len(sys.argv) < 2 and registered:
            QMessageBox.information(
                None,
                "大将怪兽",
                "右键菜单注册成功。\n请在文件上点击右键并选择“召唤大将怪兽摧毁”。",
            )
            sys.exit(0)
        message = target_error
        if registration_error:
            message += f"\n\n右键菜单注册失败：{registration_error}"
        QMessageBox.critical(None, "大将怪兽", message)
        sys.exit(1)

    ex = MonsterDeleter(target)
    ex.show()
    sys.exit(app.exec())

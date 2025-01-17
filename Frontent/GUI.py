from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QLineEdit, QGridLayout, QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QWidget
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
AssistantName = env_vars.get("AssistantName")
current_dir = os.getcwd()
old_chat_messsage = ""

TempDirPath = rf"{current_dir}\Frontent\Files"
GraphicsDirPath = rf"{current_dir}\Frontent\Graphic"


def AnswerModifier(ANswer):
    lines = ANswer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
            
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            
            
    return new_query.capitalize()

def SetMicrophonesStatus(Command):
    with open(rf'{TempDirPath}\Mic.data',"w", encoding='utf-8') as file:
        file.write(Command)
        
def GetMicrophonesStatus(Command):
    with open(rf'{TempDirPath}\Mic.data',"r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data',"w", encoding='utf-8') as file:
        file.write(Status)
        
def GetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data',"r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophonesStatus("False")
    
def MicButtonClosed():
    SetMicrophonesStatus("True")
    
def GraphicDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen(Text):
    with open (rf'{TempDirPath}\Responses.data',"w", encoding='utf-8') as file:
        file.write(Text)
        
class ChatSection(QWidget):
        def __init__(self):
            super(ChatSection, self).__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(-10, 40, 40, 100)
            layout.setSpacing(-100)
            self.chat_text_edit = QTextEdit()
            self.chat_text_edit.setReadOnly(True)
            self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
            self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
            layout.addWidget(self.chat_text_edit)
            self.setStyleSheet("background-color: black;")
            layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraints)
            layout.setStretch(1, 1)
            self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            text_color = Qt.color(Qt.blue)
            text_color_text = QTextCharFormat()
            text_color_text.setForeground(text_color)
            self.chat_text_edit.setCurrentCharFormat(text_color_text)
            self.gif_label = QLabel()
            self.gif_label.setStyleSheet("border: none;")
            movie =QMovie(GraphicsDirPath('Lyra.gif'))
            max_gif_size_W = 480
            max_gif_size_H = 270
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
            layout.addWidget(self.gif_label)
            self.label = QLabel("")
            self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
            self.label.setAlignment(Qt.AlignRight)
            layout.addWidget(self.label)
            layout.setSpacing(-10)
            layout.addWidget(self.gif_label)
            font = QFont()
            font.setPointSize(13)
            self.chat_text_editor.setFont(font)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.loadMessages)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(5)
            self.chat_text_edit.viewport().installEventFilter(self)
            self.setStyleSheet("""
                            QScrollBar:vertical{
                                border:none;
                                background: black;
                                width: 10px;
                                margin: 0px 0px 0px 0px;
                            }
                            
                            QScrollBar::handle:vertical{
                                background: white;
                                min-height: 20px;
                            }
                            
                            QScrollBar::add-line:vertical{
                                background: black;
                                subcontrol-position: bottom;
                                subcontrol-origin: margin;
                                height: 10px;
                            }
                            
                            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
                                background: none;
                                border: none;
                                color: none;
                            }
                            
                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
                                background: none;
                            }
            """)
            
            
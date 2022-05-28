import json
import os
import time

import PyQt5
import numpy
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel

from face_apis import Face_Apis
from face_recognizer import Face_Recognizer
from face_register import Face_Register

REGISTER_MODE_CODE = 0
RECOGNIZER_MODE_CODE = 1


class UI_Service:
    def __init__(self):
        self.register = Face_Register()
        self.recognizer = Face_Recognizer()
        self.face_api = Face_Apis()
        self.recognizer.get_face_database()


class Log_Bar_Service(QThread, UI_Service):
    log_bar_show = pyqtSignal(str)

    def __init__(self, main_ui_text_log_label: QLabel):
        super().__init__()
        self.main_ui_text_log_label = main_ui_text_log_label
        self.log_to_show = ""

    def run(self):
        self.__log_set_text()

    def send_log_text(self, to_show):
        self.log_to_show = to_show

    def __log_set_text(self):
        if self.main_ui_text_log_label.text() != self.log_to_show or self.main_ui_text_log_label.text() == "TextLabel":
            self.log_bar_show.emit(self.log_to_show)
        else:
            self.log_bar_show.emit(self.main_ui_text_log_label.text())


class Start_Stop_Camera_Counter_Service(QThread, UI_Service):
    def __init__(self):
        super().__init__()


class Save_Face_Service(QThread, UI_Service):
    log_bar_show = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.log_to_show = ""
        self.current_frame = None
        self.new_face_name = ""

    def run(self):
        self.__save_new_face()

    def receive_frame_and_name(self, frame, name: str):
        self.current_frame = frame
        self.new_face_name = name

    def __save_new_face(self):
        self.log_to_show = self.register.register_new_face(self.current_frame, self.new_face_name)
        self.log_bar_show.emit(self.log_to_show)


class Face_CSV_Generation_Service(QThread, UI_Service):
    def __init__(self):
        super().__init__()

    def run(self):
        self.__generate_faces_csv()

    def __generate_faces_csv(self):
        self.register.generate_faces_csv()
        self.recognizer.get_face_database()


class Face_API_Service(QThread, UI_Service):
    face_data = pyqtSignal(dict)
    face_api_finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.faces_info = {}
        self.status = False

    def run(self):
        self.status = self.__use_faces_api()
        self.face_data.emit(self.faces_info)
        self.face_api_finished.emit(self.status)
        print("api finished, signal is" + str(self.status))
        self.status = False

    def __use_faces_api(self):
        self.status = False
        self.status = self.face_api.use_all_faces_api()
        if self.status:
            with open(os.getcwd() + "\\data\\faces_info.json", 'r') as json_file:
                self.faces_info = json.load(json_file)
            return True
        else:
            return False


class Face_Recognition_Service(QThread, UI_Service):
    reco_result = pyqtSignal(PyQt5.QtGui.QPixmap)
    log_bar_show = pyqtSignal(str)
    name_list_show = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.current_frame = None
        self.log_to_show = ""
        self.name_list = []
        self.show_frame = None

    def run(self):
        self.__frame_reco()
        self.reco_result.emit(self.show_frame)
        self.log_bar_show.emit(self.log_to_show)
        self.name_list_show.emit(self.name_list)

    def get_current_frame(self, current_frame: numpy.ndarray):
        self.current_frame = current_frame

    def __frame_reco(self):
        self.log_to_show, self.name_list, show = self.recognizer.recognize_current_frame(self.current_frame)
        show = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.show_frame = QtGui.QPixmap.fromImage(show)


class Face_Register_Service(QThread, UI_Service):
    reco_result = pyqtSignal(PyQt5.QtGui.QPixmap)
    log_bar_show = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_frame = None
        self.log_to_show = ""
        self.show_frame = None

    def run(self):
        self.__frame_regi()
        self.reco_result.emit(self.show_frame)
        self.log_bar_show.emit(self.log_to_show)

    def get_current_frame(self, current_frame: numpy.ndarray):
        self.current_frame = current_frame

    def __frame_regi(self):
        self.log_to_show, show = self.register.show_faces_detection(self.current_frame)
        show = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.show_frame = QtGui.QPixmap.fromImage(show)


class UI_Delay_Operation_Service(QThread):
    sleep_finish_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.delay_sec = 0.0

    def run(self):
        time.sleep(self.delay_sec)
        self.delay_sec = 0.0
        self.sleep_finish_signal.emit(True)

    def set_sleep_secs(self, to_sleep_secs: float):
        self.delay_sec = to_sleep_secs

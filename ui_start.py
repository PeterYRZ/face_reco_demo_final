import sys

import PyQt5
import cv2
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction

from face_apis import Face_Apis
from face_recognizer import Face_Recognizer
from window_main import *
from ui_tasks_thread import Log_Bar_Service, Save_Face_Service, Face_CSV_Generation_Service, Face_API_Service, \
    Face_Recognition_Service, Face_Register_Service, UI_Delay_Operation_Service
from ui_single_image_thread import *
from ui_face_aging_thread import *
from destiny_measure import *

REGISTER_MODE_CODE = 0
RECOGNIZER_MODE_CODE = 1


class Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_log = ""
        self.timer_camera = QtCore.QTimer()
        self.image = None
        self.setupUi(self)
        self.setWindowTitle("人脸识别身份认证系统")
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.register = Face_Register()
        self.recognizer = Face_Recognizer()
        self.function_tag = REGISTER_MODE_CODE
        self.face_api = Face_Apis()
        self.faces_info = {}
        self.single_image_dialog_window = Ui_Single_Image_Window()
        self.face_aging_dialog_window = Ui_Face_Aging_Window()
        self.current_name_list = []
        # 管理log_bar的信号
        self.log_bar_service = Log_Bar_Service(main_ui_text_log_label=self.log_window)
        self.log_bar_service.log_bar_show.connect(self.__log_text_set)

        # 管理save_new_face的按钮
        self.save_face_service = Save_Face_Service()

        # 管理生成csv文件的按钮
        self.face_csv_generator_service = Face_CSV_Generation_Service()

        # 管理Face_API的信号
        self.face_api_service = Face_API_Service()
        self.face_api_service.face_data.connect(self.__faces_info_get)
        self.face_api_service.face_api_finished.connect(self.__start_destiny_measurement)

        # 管理人脸识别结果的信号
        self.face_recognition_service = Face_Recognition_Service()
        self.face_recognition_service.name_list_show.connect(self.__change_current_person_label)
        self.face_recognition_service.log_bar_show.connect(self.__log_text_set)
        self.face_recognition_service.reco_result.connect(self.__video_frame_show)

        # 管理人脸录入结果的信号
        self.face_register_service = Face_Register_Service()
        self.face_register_service.log_bar_show.connect(self.__log_text_set)
        self.face_register_service.reco_result.connect(self.__video_frame_show)

        # 管理算命模块，因为有阻塞，异步进行
        self.destiny_measurement_service = Destiny_Measure_Service()
        self.destiny_measurement_service.face_json_info.connect(self.__faces_info_get)

        # 调用API后一定时间的延迟信号
        self.face_api_btn_delay_service = UI_Delay_Operation_Service()
        self.face_api_btn_delay_service.sleep_finish_signal.connect(self.__change_api_btn_to_true)

        # 管理单张照片识别的线程

        try:
            with open(os.getcwd() + "\\data\\faces_info.json", 'r') as json_file:
                self.faces_info = json.load(json_file)
        except:
            self.faces_info = {}

        self.__init_actions()
        self.__init_menu_bar()
        self.__connect_actions()
        self.__slot_init()
        self.show()

    def __init_menu_bar(self):
        menu_bar = self.menuBar()
        about_menu = menu_bar.addMenu("&关于")
        about_menu.addAction(self.show_about_action)
        about_menu.addAction(self.quit_action)

    def __init_actions(self):
        self.show_about_action = QAction("&关于本软件", self)
        self.quit_action = QAction("&退出", self)

    def __connect_actions(self):
        self.show_about_action.triggered.connect(self.__show_about_implement)
        self.quit_action.triggered.connect(self.__quit_application)

    def __show_about_implement(self):
        message = "关于本项目：\n人脸识别身份认证系统\n项目参与者：余任之；肖仲煜\n开发者：余任之\nCopyright © 2022 Yu Renzhi 余任之. All rights " \
                  "reserved.\n联系方式：peterrolls@qq.com "
        QMessageBox.about(self, "关于", message)

    def __quit_application(self):
        self.close()

    def __slot_init(self):
        self.btn_login_start.clicked.connect(lambda: self.__start_stop_camera_counter())
        self.timer_camera.timeout.connect(lambda: self.__show_camera())
        self.btn_take_pic.clicked.connect(lambda: self.__save_face())
        self.btn_login_end.clicked.connect(lambda: self.__end_registration_csv())
        self.btn_reco_start.clicked.connect(lambda: self.__start_recognizer())
        self.btn_start_apis.clicked.connect(lambda: self.__start_apis())
        self.btn_open_single_pic.clicked.connect(lambda: self.__open_single_image_dialog())
        self.btn_open_aging_faces_page.clicked.connect(lambda: self.__open_face_aging_dialog())
        self.btn_show_destiny.clicked.connect(lambda: self.__destiny_show_message_box())
        # 按钮状态初始化
        # self.btn_open_aging_faces_page.setVisible(False)
        self.btn_take_pic.setEnabled(False)
        self.btn_show_destiny.setEnabled(False)
        self.btn_login_end.setEnabled(False)
        self.btn_reco_start.setEnabled(False)

    def __log_text_set(self, to_show):
        self.log_window.setText(to_show)

    def __start_login(self):
        pass

    def __start_stop_camera_counter(self):
        print('enter method')
        if not self.timer_camera.isActive():  # 若定时器未启动
            print('enter not activate counter')
            flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
            if not flag:  # flag表示open()成不成功
                print('enter not successful')
                msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查相机与电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok)
                print(msg)
            else:
                print('activate counter')
                self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                self.function_tag = REGISTER_MODE_CODE
                self.btn_take_pic.setEnabled(True)
                self.btn_reco_start.setEnabled(True)
        else:
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.camera_show.clear()  # 清空视频显示区域
            self.btn_take_pic.setEnabled(False)
            self.btn_show_destiny.setEnabled(False)
            self.btn_login_end.setEnabled(False)
            self.btn_reco_start.setEnabled(False)
            self.current_person.setText("")
            self.log_window.setText("日志窗口")
            self.current_person.setText("当前识别人信息")
            self.camera_show.setText("相机视频流")

    def __get_current_frame(self):
        flag, self.image = self.cap.read()  # 从视频流中读取

        show = cv2.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
        return show

    def __show_camera(self):
        show = self.__get_current_frame()
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        if self.function_tag == REGISTER_MODE_CODE:
            self.face_register_service.get_current_frame(show)
            self.face_register_service.start()
        if self.function_tag == RECOGNIZER_MODE_CODE:
            self.face_recognition_service.get_current_frame(show)
            self.face_recognition_service.start()

    def __video_frame_show(self, frame: PyQt5.QtGui.QPixmap):
        self.camera_show.setPixmap(frame)

    def __save_face(self):
        self.edit_name.setEnabled(False)
        self.btn_login_end.setEnabled(True)
        save = self.__get_current_frame()
        face_name = self.edit_name.text()
        self.save_face_service.receive_frame_and_name(save, face_name)
        self.save_face_service.start()

    def __end_registration_csv(self):
        self.edit_name.setEnabled(True)
        self.btn_login_end.setEnabled(False)
        self.btn_take_pic.setEnabled(True)
        self.face_csv_generator_service.start()

    def __start_recognizer(self):
        self.btn_show_destiny.setEnabled(True)
        self.btn_reco_start.setEnabled(False)
        if self.function_tag == REGISTER_MODE_CODE:
            self.recognizer.get_face_database()
        self.function_tag = RECOGNIZER_MODE_CODE

    def __start_apis(self):
        print("start apis")
        self.btn_start_apis.setEnabled(False)
        self.face_api_btn_delay_service.set_sleep_secs(3.0)
        self.face_api_service.start()
        self.face_api_btn_delay_service.start()

    def __start_destiny_measurement(self, status: bool):
        if status:
            print("start destiny")
            self.destiny_measurement_service.start()
        else:
            message = "faces_info.json 无权写入，请检查您对此文件权限的设置"
            QMessageBox.about(self, "API调用错误", message)

    def __faces_info_get(self, face_data: dict):
        self.faces_info = face_data

    def __change_current_person_label(self, name_list):
        self.current_name_list = name_list
        label_to_show = ""
        for names in name_list:
            try:
                this_info = self.faces_info[names]
                label_to_show = label_to_show + names + ":\n性别：" + this_info['性别'] + "\n年龄：" + str(
                    this_info['年龄']) + "岁\n人种：" + this_info['人种'] + "\n颜值打分：" + str(this_info['颜值评分']) + "/100分\n"
            except KeyError:
                pass
        self.current_person.setText(label_to_show)

    def __open_single_image_dialog(self):
        self.single_image_dialog_window.show()

    def __open_face_aging_dialog(self):
        self.face_aging_dialog_window.show()

    def __destiny_show_message_box(self):
        message = ""
        for names in self.current_name_list:
            if "运势" in self.faces_info[names]:
                this_message = str(self.faces_info[names]["运势"])
                message = message + this_message + "\n"
        QMessageBox.about(self, "运势", message)

    def __change_api_btn_to_true(self, signal: bool):
        if signal:
            self.btn_start_apis.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.getcwd() + '\\icons8_male_user.ico'))
    with open(os.getcwd() + '\\dark_teal.qss', 'r') as file:
        app.setStyleSheet(file.read())
    form = QMainWindow()
    window = Ui_MainWindow()
    sys.exit(app.exec_())

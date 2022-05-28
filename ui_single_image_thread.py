import base64
import math
import tkinter.filedialog

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from ui_single_pic import *


class Ui_Single_Image_Window(QWidget, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("单张人像颜值评测")
        self.image = None
        self.result = ""
        # 。。。。
        self.image_analysis_service = Image_Analysis_Service()
        self.image_analysis_service.result_string.connect(self.__set_result)

        self.__slot_init()

    def __slot_init(self):
        self.btn_import_image.clicked.connect(lambda: self.__select_image())

    def __select_image(self):
        root = tkinter.Tk()  # 创建一个Tkinter.Tk()实例
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        file_path = tkinter.filedialog.askopenfilename(title=u'选择文件')
        f = open(file_path, 'rb')
        self.pic_show.setPixmap(QPixmap(file_path))
        self.pic_show.setScaledContents(True)
        self.image = base64.b64encode(f.read()).decode('utf-8')
        self.image_analysis_service.get_image_to_analysis(image=self.image)
        self.image_analysis_service.start()
        # return self.image

    def __set_result(self, result: str):
        self.result_show.setText(result)


class Single_Image_Dialog_Service:
    def __init__(self):
        self.dialog_window = None
        self.signal_face_api = Single_Face_Api()

    def get_dialog_window(self, dialog_window: Ui_Single_Image_Window):
        self.dialog_window = dialog_window


class Image_Analysis_Service(QThread, Single_Image_Dialog_Service):
    result_string = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.image = None
        self.api_result = ""

    def run(self):
        self.__get_api_result()
        self.result_string.emit(self.api_result)

    def get_image_to_analysis(self, image):
        self.image = image

    def __get_api_result(self):
        self.api_result = self.signal_face_api.api_result(self.image)


class Single_Face_Api:
    def __init__(self):
        self.client_id = 'FfPyoqAzmhmUSOITZFL7iU7W'  # ak
        self.client_secret = 'GHbKMGqny18jLaBy3utNGLPyqAiFLDeB'
        self.result = ""

    def __get_access_token(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + self.client_id + '&client_secret=' + self.client_secret
        header = {'Content-Type': 'application/json; charset=UTF-8'}
        response1 = requests.post(url=host, headers=header)  # <class 'requests.models.Response'>
        json1 = response1.json()  # <class 'dict'>
        access_token = json1['access_token']

        return access_token

    def __bd_rec_face(self, image_base64):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        params = {"image": image_base64, "image_type": "BASE64",
                  "face_field": "age,beauty,glasses,gender,race,expression"}
        header = {'Content-Type': 'application/json'}

        access_token = self.__get_access_token()  # '[调用鉴权接口获取的token]'
        request_url = request_url + "?access_token=" + access_token

        request_url = request_url + "?access_token=" + access_token
        response1 = requests.post(url=request_url, data=params, headers=header)
        json1 = response1.json()
        # self.result = "性别为:" + str(json1["result"]["face_list"][0]['gender']['type']) + \
        #               "\n年龄为:" + str(json1["result"]["face_list"][0]['age']) + "岁" + \
        #               "\n人种为:" + str(json1["result"]["face_list"][0]['race']['type']) + \
        #               "\n颜值评分为:" + str(Single_Face_Api.score_add(json1["result"]["face_list"][0]['beauty'])) + '分/100分' + \
        #               "\n是否带眼镜:" + str(json1["result"]["face_list"][0]['glasses']['type']) + \
        #               "\n图片中包含人物表情:" + str(json1["result"]["face_list"][0]['expression']['type'])
        self.result = "性别为:" + str(json1["result"]["face_list"][0]['gender']['type']) + \
                      "\n年龄为:" + str(json1["result"]["face_list"][0]['age']) + "岁" + \
                      "\n人种为:" + str(json1["result"]["face_list"][0]['race']['type']) + \
                      "\n颜值评分为:" + str(Single_Face_Api.score_add(json1["result"]["face_list"][0]['beauty'])) + '分/100分'

    def api_result(self, image_base64):
        self.__bd_rec_face(image_base64=image_base64)
        return self.result

    @staticmethod
    def score_add(current_score: float):
        if current_score <= 20:
            multi_factor = 1.0
        else:
            multi_factor = -0.879 * math.log(current_score) + 5.0515
        result_score = current_score * multi_factor
        if result_score > 100.0:
            result_score = 100.0
        elif result_score < 0:
            result_score = 0.0
        return round(result_score, 2)
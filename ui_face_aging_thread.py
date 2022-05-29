import csv
import json
import os
import cv2 as cv
import tkinter.filedialog
import dlib

import numpy as np
import paddle

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ui_import_image import *
from paddle_gan.ppgan.apps import Pixel2Style2PixelPredictor, StyleGANv2EditingPredictor
from PIL import Image
from face_register import Face_Register


class Ui_Face_Aging_Window(QWidget, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("跨年龄段面部导入与生成")
        self.selected_image = None
        self.selected_image_path = None
        self.new_face_name = ""
        self.aging_json_info_path = os.getcwd() + "\\data\\aging_info.json"
        self.aging_info = {}
        self.aging_args_list = [2, 3, 4, 5, 7, 9]
        self.faces_list = []
        # 老化模型生成线程
        self.face_aging_model_service = Face_Aging_Model_Service()
        self.face_aging_model_service.result_npy_file.connect(self.__npy_path_json_modify)
        self.face_aging_model_service.combination_image_path.connect(self.__show_aging_result)
        self.face_aging_model_service.is_generating_finished.connect(self.__control_input_btn_enable)
        self.face_aging_model_service.log_to_show.connect(self.__log_text_set)
        self.aging_npy_path = ""

        # 单张照片人脸比对
        self.aging_reco_service = Aging_Reco_Service()
        self.aging_reco_service.log_to_show.connect(self.__log_text_set)
        self.aging_reco_service.to_reco_image_show.connect(self.__show_to_reco_image)
        self.aging_reco_service.result_face_name.connect(self.__show_reco_result_ori_image)

        self.__slot_init()

    def __slot_init(self):
        self.import_image.clicked.connect(lambda: self.__select_image())
        self.generate_old.clicked.connect(lambda: self.__generate_image_old())
        self.btn_input_to_reco_image.clicked.connect(lambda: self.__face_comparing())
        self.generate_old.setEnabled(False)
        self.sync_json.setEnabled(False)

    def __to_import_image_display(self, stored_image_path: str):
        self.to_import_image_show.setPixmap(QPixmap(stored_image_path))

    def __npy_path_json_modify(self, current_npy_path: str):
        self.aging_npy_path = current_npy_path
        try:
            with open(self.aging_json_info_path, 'r') as aging_json:
                self.aging_info = json.load(aging_json)
        except FileNotFoundError:
            with open(self.aging_json_info_path, 'w+') as aging_json:
                pass
        finally:
            with open(self.aging_json_info_path, 'w+') as aging_json:
                if not self.new_face_name.encode('utf-8').decode() in self.aging_info:
                    self.aging_info[self.new_face_name.encode('utf-8').decode()] = {}
                self.aging_info[self.new_face_name.encode('utf-8').decode()]["npy"] = current_npy_path
                aging_json.truncate()
                json.dump(self.aging_info, aging_json, indent=4, ensure_ascii=False)

    def __select_image(self):
        root = tkinter.Tk()  # 创建一个Tkinter.Tk()实例
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        self.selected_image_path = tkinter.filedialog.askopenfilename(title=u'选择要导入的基准图片')
        self.selected_image = open(self.selected_image_path, 'rb')
        self.to_import_image_show.setPixmap(QPixmap(self.selected_image_path))
        self.to_import_image_show.setScaledContents(True)

        self.new_face_name = self.name_edit.text()
        target_dir = os.getcwd() + "\\data\\face_aging_npy\\" + self.new_face_name
        if not os.path.exists(target_dir):
            if not os.path.exists(os.getcwd() + "\\data\\face_aging_npy\\"):
                os.mkdir(os.getcwd() + "\\data\\face_aging_npy\\")
            os.mkdir(os.getcwd() + "\\data\\face_aging_npy\\" + self.new_face_name)
        image_save = cv.imdecode(np.fromfile(self.selected_image_path, dtype=np.uint8), -1)
        cv.imencode('.jpg', image_save)[1].tofile(target_dir + "\\" + self.new_face_name + ".jpg")
        # cv.imwrite(target_dir + "\\" + self.new_face_name + ".jpg", image_save)
        self.selected_image_path = target_dir + "\\" + self.new_face_name + ".jpg"
        self.__to_import_image_display(self.selected_image_path)
        self.generate_old.setEnabled(True)

    def __generate_image_old(self):
        self.face_aging_model_service.init(origin_image_path=self.selected_image_path,
                                           image_face_name=self.new_face_name,
                                           aging_args_list=self.aging_args_list)
        self.face_aging_model_service.start()
        self.btn_input_to_reco_image.setEnabled(False)

    def __show_aging_result(self, combination_image_path: str):
        self.generated_images_show.setPixmap(QPixmap(combination_image_path))
        self.generated_images_show.setScaledContents(True)
        # self.__get_all_aging_csv()

    def __face_comparing(self):
        root = tkinter.Tk()  # 创建一个Tkinter.Tk()实例
        root.withdraw()  # 将Tkinter.Tk()实例隐藏
        selected_image_path = tkinter.filedialog.askopenfilename(title=u'选择要跨年龄识别的图片')
        if selected_image_path is None:
            return
        else:
            self.aging_reco_service.init(selected_image_path=selected_image_path)
            self.aging_reco_service.start()

    def __show_to_reco_image(self, import_image: QPixmap):
        self.generated_images_show.setPixmap(import_image)
        self.generated_images_show.setScaledContents(True)

    def __log_text_set(self, log_text: str):
        self.log_text.setText(log_text)

    def __show_reco_result_ori_image(self, person_name: str):
        if os.path.exists(os.getcwd() + "\\data\\face_aging_npy\\" + person_name + "\\" + person_name + ".jpg"):
            self.to_import_image_show.setPixmap(QPixmap(
                os.getcwd() + "\\data\\face_aging_npy\\" + person_name + "\\" + person_name + ".jpg"
            ))
            self.to_import_image_show.setScaledContents(True)

    def __control_input_btn_enable(self, is_enable: bool):
        self.btn_input_to_reco_image.setEnabled(is_enable)


class Face_Aging_Model_Service(QThread):
    result_npy_file = pyqtSignal(str)
    combination_image_path = pyqtSignal(str)
    is_generating_finished = pyqtSignal(bool)
    log_to_show = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.origin_image_path = ""
        self.image_face_name = ""
        self.npy_file_path = ""
        self.aging_args_list = []
        self.face_register = Face_Register()

    def run(self):
        npy_file_exists = self.__generate_npy_file_path()
        self.log_to_show.emit("start generating npy file")
        print("start generating npy file")
        if npy_file_exists:
            self.log_to_show.emit("face aging model exists, skipping generation")
            print("face aging model exists, skipping generation")
        else:
            self.__generate_face_npy_file()
            self.log_to_show.emit("npy file generation completed")
            print("npy file generation completed")
        self.result_npy_file.emit(self.npy_file_path + "\\dst.npy")
        # self.ori_image_path.emit(self.origin_image_path)
        self.log_to_show.emit("starting generating aging faces using cpu")
        print("starting generating aging faces using cpu")
        self.__aging_faces_generate()
        self.log_to_show.emit("aging faces generation completed")
        print("aging faces generation completed")
        self.__img_combination()
        self.combination_image_path.emit(self.npy_file_path + "\\aging_combination.png")
        self.log_to_show.emit("image combination completed")
        print("image combination completed")
        self.__get_all_aging_csv()
        self.log_to_show.emit("csv file generated")
        print("csv file generated")
        self.is_generating_finished.emit(True)

    def init(self, origin_image_path: str, image_face_name: str, aging_args_list=None):
        if aging_args_list is None:
            aging_args_list = [2, 3, 4, 5, 7, 9]
        self.origin_image_path = origin_image_path
        self.image_face_name = image_face_name
        self.aging_args_list = aging_args_list

    def __generate_npy_file_path(self):
        self.npy_file_path = os.getcwd() + "\\data\\face_aging_npy\\" + self.image_face_name
        if not os.path.exists(self.npy_file_path):
            if not os.path.exists(os.getcwd() + "\\data\\face_aging_npy\\"):
                os.mkdir(os.getcwd() + "\\data\\face_aging_npy\\")
            os.mkdir(self.npy_file_path)
        return os.path.exists(self.npy_file_path + "\\dst.npy")

    def __generate_face_npy_file(self):
        paddle.set_device('cpu')
        predictor = Pixel2Style2PixelPredictor(
            output_path=self.npy_file_path,
            weight_path=None,
            model_type="ffhq-inversion",
            seed=233,
            size=1024,
            style_dim=512,
            n_mlp=8,
            channel_multiplier=2)
        predictor.run(self.origin_image_path)

    def __aging_faces_generate(self):
        paddle.set_device('cpu')
        predictor = StyleGANv2EditingPredictor(
            output_path=self.npy_file_path,
            weight_path=None,
            model_type="ffhq-config-f",
            seed=None,
            size=1024,
            style_dim=512,
            n_mlp=8,
            channel_multiplier=2,
            direction_path=None)
        for i in range(len(self.aging_args_list)):
            if os.path.exists(self.npy_file_path + "\\src.editing.png"):
                try:
                    os.remove(self.npy_file_path + "\\dst.editing.png")
                finally:
                    os.remove(self.npy_file_path + "\\dst.editing.npy")
                    os.remove(self.npy_file_path + "\\src.editing.png")
            predictor.run(self.npy_file_path + "\\dst.npy", "age", self.aging_args_list[i])
            os.rename(src=self.npy_file_path + "\\dst.editing.png",
                      dst=self.npy_file_path + "\\" + str(self.aging_args_list[i]) + ".png")
            os.remove(self.npy_file_path + "\\dst.editing.npy")
            os.remove(self.npy_file_path + "\\src.editing.png")

    def __img_combination(self):
        image_files = []
        for index in range(3 * 2):
            image_files.append(Image.open(os.getcwd() + "\\data\\face_aging_npy\\" + self.image_face_name + "\\" + str(
                self.aging_args_list[index]) + ".png"))  # 读取所有用于拼接的图片
        target = Image.new('RGB', (1024 * 3, 1024 * 2))  # 创建成品图的画布
        # 第一个参数RGB表示创建RGB彩色图，第二个参数传入元组指定图片大小，第三个参数可指定颜色，默认为黑色
        for row in range(2):
            for col in range(3):
                target.paste(image_files[3 * row + col], (0 + 1024 * col, 0 + 1024 * row))
        target.save(self.npy_file_path + "\\aging_combination.png", quality=50)  # 成品图保存

    def __get_all_aging_csv(self):
        person_list = os.listdir("data\\face_aging_npy")
        person_list.sort()
        with open("data\\agings_all.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for names in person_list:
                for index in self.aging_args_list:
                    person_feature = self.face_register.return_128d_features(
                        os.getcwd() + "\\data\\face_aging_npy\\" + str(names) + "\\" + str(index) + ".png")
                    person_feature = np.array(person_feature, dtype=object)
                    person_feature = np.insert(person_feature, 0, names + "-" + str(index), axis=0)
                    writer.writerow(person_feature)


class Aging_Reco_Service(QThread):
    to_reco_image_show = pyqtSignal(QPixmap)
    log_to_show = pyqtSignal(str)
    result_face_name = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.aging_args_list = [2, 3, 4, 5, 7, 9]
        self.selected_image = None
        self.selected_image_path = ""
        self.dlib_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
        self.face_reco_model = dlib.face_recognition_model_v1(
            "data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")
        self.faces_database = []
        self.faces_list_known = []

    def run(self):
        # self.__import_to_reco_image()
        print("import to reco image completed")
        self.__get_aging_database()
        print("get aging database finished")
        print(str(self.faces_database))
        print(str(self.faces_list_known))
        self.__recognize_face_input()
        print("reco completed")

    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist

    def init(self, selected_image_path: str):
        self.selected_image_path = selected_image_path
        self.selected_image = open(self.selected_image_path, 'rb')
        self.to_reco_image_show.emit(QPixmap(self.selected_image_path))

    def __get_aging_database(self):
        if os.path.exists("data\\agings_all.csv"):
            path_features_known_csv = "data\\agings_all.csv"
            csv_rd = pd.read_csv(path_features_known_csv, header=None)
            for i in range(csv_rd.shape[0]):
                features_someone_arr = []
                self.faces_list_known.append(csv_rd.iloc[i][0].encode('utf-8').decode())
                for j in range(1, 129):
                    if csv_rd.iloc[i][j] == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(csv_rd.iloc[i][j])
                self.faces_database.append(features_someone_arr)
            return 1
        else:
            return 0

    def __recognize_face_input(self):
        this_image_faces = []
        current_image_faces = []
        current_image_faces_position = []
        # img_rd = cv.imread(self.selected_image_path)
        img_rd = cv.imdecode(np.fromfile(self.selected_image_path, dtype=np.uint8), -1)
        faces = self.dlib_detector(img_rd, 1)
        if len(faces) != 0:
            for i in range(len(faces)):
                shape = self.predictor(img_rd, faces[i])
                this_image_faces.append(self.face_reco_model.compute_face_descriptor(img_rd, shape))
            for k in range(len(faces)):
                current_image_faces.append("---")
                current_image_faces_position.append(tuple(
                    [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]
                ))
                current_img_e_distance_list = []
                for i in range(len(self.faces_list_known)):
                    if str(self.faces_database[i][0]) != "0.0":
                        e_distance_tmp = self.return_euclidean_distance(this_image_faces[k],
                                                                        self.faces_database[i])
                        current_img_e_distance_list.append(e_distance_tmp)
                    else:
                        current_img_e_distance_list.append(999999999)
                print(current_img_e_distance_list)
                similar_person_num = current_img_e_distance_list.index(min(current_img_e_distance_list))
                if min(current_img_e_distance_list) < 0.6:
                    current_image_faces[k] = self.faces_list_known[similar_person_num]
        self.log_to_show.emit(str(current_image_faces))
        print(str(current_image_faces[0]).split("-")[0])
        self.result_face_name.emit(str(current_image_faces[0]).split("-")[0])

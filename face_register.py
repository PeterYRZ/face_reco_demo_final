import csv

import cv2
import dlib
import os
import numpy as np


class Face_Register:
    def __init__(self):
        self.registed_face_photo_path = "data/data_faces/"
        self.dlib_detector = dlib.get_frontal_face_detector()
        self.current_frame = None
        self.predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
        self.face_reco_model = dlib.face_recognition_model_v1(
            "data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

        self.existing_faces = []
        self.existing_faces_num = 0  # 已经录入的脸数

    def show_faces_detection(self, current_frame):
        """
        读入视频帧，使用dlib正向人脸检测器进行人脸识别，返回标记的视频帧
        :param current_frame: 从cv2.VideoCapture(0).read()中获取到的图像
        :return: to_show_log 输出的实时日志; current_frame 处理后的视频帧
        """
        to_show_log = ""
        faces = self.dlib_detector(current_frame, 0)

        if len(faces) != 0:
            # 矩形框
            for k, d in enumerate(faces):
                # 计算矩形框大小
                height = (d.bottom() - d.top())
                width = (d.right() - d.left())
                hh = int(height / 2)
                ww = int(width / 2)

                # 判断人脸矩形框是否超出边界
                if (d.right() + ww) > 640 or (d.bottom() + hh > 480) or (d.left() - ww < 0) or (d.top() - hh < 0):
                    color_rectangle = (255, 0, 0)
                    to_show_log = "超出范围"
                else:
                    color_rectangle = (255, 255, 255)

                cv2.rectangle(current_frame,
                              tuple([d.left() - ww, d.top() - hh]),
                              tuple([d.right() + ww, d.bottom() + hh]),
                              color_rectangle, 2)
        return to_show_log, current_frame

    def register_new_face(self, current_frame, new_face_name):
        """
        读入视频帧，使用dlib正向人脸检测器进行人脸识别，并保存当中的人脸
        :param current_frame: 从cv2.VideoCapture(0).read()中获取到的图像
        :param new_face_name: 将要登记的人脸的名字
        :return: log_to_show 输出的实时日志;
        """
        target_dir = os.getcwd() + "\\data\\data_faces\\" + new_face_name
        if not os.path.exists(target_dir):
            os.mkdir(os.getcwd() + "\\data\\data_faces\\" + new_face_name)
        this_picture_number = self.__get_dir_imgs_num(target_dir) + 1
        faces = self.dlib_detector(current_frame, 0)
        log_to_show = ""
        if len(faces) != 0:
            print(len(faces))
            for k, d in enumerate(faces):
                height = (d.bottom() - d.top())
                width = (d.right() - d.left())
                hh = int(height / 2)
                ww = int(width / 2)

                # 判断人脸矩形框是否超出边界
                if (d.right() + ww) > 640 or (d.bottom() + hh > 480) or (d.left() - ww < 0) or (d.top() - hh < 0):
                    log_to_show = "超出范围"
                    print("超出范围")
                else:
                    img_blank = np.zeros((int(height * 2), width * 2, 3), np.uint8)
                    for ii in range(height * 2):
                        for jj in range(width * 2):
                            img_blank[ii][jj] = current_frame[d.top() - hh + ii][d.left() - ww + jj]
                    cv2.imencode('.jpg', img_blank)[1].tofile(
                        os.getcwd() + "\\data\\data_faces\\" + new_face_name + "\\" + str(this_picture_number) + ".jpg")
                    # cv2.imwrite(
                    #     os.getcwd() + "\\data\\data_faces\\" + new_face_name + "\\" + str(this_picture_number) + ".jpg",
                    #     img_blank)
                    log_to_show = "已经保存"
                    print("已经保存")
        return log_to_show

    def __get_existing_face(self):
        self.existing_faces = []
        for file in os.listdir(os.getcwd() + "\\data\\data_faces"):
            m = os.path.join(os.getcwd() + "\\data\\data_faces", file)
            if os.path.isdir(m):
                self.existing_faces.append(os.path.split(m)[1])
        self.existing_faces_num = len(self.existing_faces)

    @staticmethod
    def __get_dir_imgs_num(target_dir):
        imgs_list = []
        for file in os.listdir(target_dir):
            m = os.path.join(target_dir, file)
            if not os.path.isdir(m):
                imgs_list.append(os.path.split(m)[1])
        return len(imgs_list)

    def return_128d_features(self, img_path):
        """
        输入图像路径，返回该人脸图像的128D特征
        :param img_path: 拟生成128D特征的图像的路径
        :return: face_descripor 描述脸128D特征的值numpy.ndarray
        """
        # img_rd = cv2.imread(img_path)
        img_rd = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
        # 灰度图处理
        # img_rd = cv2.cvtColor(img_rd, cv2.COLOR_BGR2GRAY)

        faces = self.dlib_detector(img_rd, 1)

        # 因为有可能截下来的人脸再去检测，检测不出来人脸了, 所以要确保是 检测到人脸的人脸图像拿去算特征
        if len(faces) != 0:
            shape = self.predictor(img_rd, faces[0])
            face_descriptor = self.face_reco_model.compute_face_descriptor(img_rd, shape)
        else:
            face_descriptor = 0
        return face_descriptor

    def __return_fratures_mean_person(self, face_name):
        features_list_personX = []
        photos_list = os.listdir(os.getcwd() + "\\data\\data_faces\\" + face_name)
        if photos_list:
            for i in range(len(photos_list)):
                # 调用 return_128d_features() 得到 128D 特征 / Get 128D features for single image of personX
                features_128d = self.return_128d_features(
                    os.getcwd() + "\\data\\data_faces\\" + face_name + "\\" + photos_list[i])
                # 遇到没有检测出人脸的图片跳过 / Jump if no face detected from image
                if features_128d == 0:
                    i += 1
                else:
                    features_list_personX.append(features_128d)

        # 计算 128D 特征的均值 / Compute the mean
        # personX 的 N 张图像 x 128D -> 1 x 128D
        if features_list_personX:
            features_mean_personX = np.array(features_list_personX, dtype=object).mean(axis=0)
        else:
            features_mean_personX = np.zeros(128, dtype=object, order='C')
        return features_mean_personX

    def generate_faces_csv(self):
        person_list = os.listdir("data\\data_faces")
        person_list.sort()

        with open("data/features_all.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for person in person_list:
                # Get the mean/average features of face/personX, it will be a list with a length of 128D
                features_mean_personX = self.__return_fratures_mean_person(person)

                features_mean_personX = np.insert(features_mean_personX, 0, person, axis=0)
                # features_mean_personX will be 129D, person name + 128 features
                writer.writerow(features_mean_personX)

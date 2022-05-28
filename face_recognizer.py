import os
import cv2
import dlib
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


class Face_Recognizer:
    def __init__(self):
        self.dlib_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
        self.face_reco_model = dlib.face_recognition_model_v1(
            "data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")
        self.face_feature_known_list = []
        self.face_name_known_list = []
        self.current_frame_face_cnt = 0  # 存储当前摄像头中捕获到的人脸数
        self.current_frame_face_feature_list = []  # 存储当前摄像头中捕获到的人脸特征
        self.current_frame_face_name_list = []  # 存储当前摄像头中捕获到的所有人脸的名字
        self.current_frame_face_name_position_list = []  # 存储当前摄像头中捕获到的所有人脸的名字坐标
        self.font = cv2.FONT_ITALIC
        self.font_chinese = ImageFont.truetype("simsun.ttc", 30)
        self.faces_info = {}

    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist

    def get_face_database(self):
        if os.path.exists("data\\features_all.csv"):
            path_features_known_csv = "data\\features_all.csv"
            csv_rd = pd.read_csv(path_features_known_csv, header=None)
            for i in range(csv_rd.shape[0]):
                features_someone_arr = []
                self.face_name_known_list.append(csv_rd.iloc[i][0].encode('utf-8').decode())
                for j in range(1, 129):
                    if csv_rd.iloc[i][j] == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(csv_rd.iloc[i][j])
                self.face_feature_known_list.append(features_someone_arr)
            return 1
        else:
            return 0

    def draw_name(self, to_draw_img):
        img = Image.fromarray(cv2.cvtColor(to_draw_img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        for i in range(self.current_frame_face_cnt):
            draw.text(xy=self.current_frame_face_name_position_list[i], text=self.current_frame_face_name_list[i],
                      font=self.font_chinese,
                      fill=(255, 255, 0))
            img_rd = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_rd

    def recognize_current_frame(self, current_frame):
        self.get_face_database()
        faces = self.dlib_detector(current_frame, 0)
        if len(faces) != 0:
            # 3. 获取当前捕获到的图像的所有人脸的特征
            for i in range(len(faces)):
                shape = self.predictor(current_frame, faces[i])
                self.current_frame_face_feature_list.append(
                    self.face_reco_model.compute_face_descriptor(current_frame, shape))
            # 4. 遍历捕获到的图像中所有的人脸 / Traversal all the faces in the database
            for k in range(len(faces)):
                # 先默认所有人不认识，是 unknown / Set the default names of faces with "unknown"
                self.current_frame_face_name_list.append("unknown")

                # 每个捕获人脸的名字坐标 / Positions of faces captured
                self.current_frame_face_name_position_list.append(tuple(
                    [faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))

                # 5. 对于某张人脸，遍历所有存储的人脸特征
                # For every faces detected, compare the faces in the database
                current_frame_e_distance_list = []
                for i in range(len(self.face_feature_known_list)):
                    # 如果 person_X 数据不为空
                    if str(self.face_feature_known_list[i][0]) != '0.0':
                        e_distance_tmp = self.return_euclidean_distance(self.current_frame_face_feature_list[k],
                                                                        self.face_feature_known_list[i])
                        current_frame_e_distance_list.append(e_distance_tmp)
                    else:
                        # 空数据 person_X
                        current_frame_e_distance_list.append(999999999)
                # 6. 寻找出最小的欧式距离匹配 / Find the one with minimum e-distance
                similar_person_num = current_frame_e_distance_list.index(min(current_frame_e_distance_list))

                if min(current_frame_e_distance_list) < 0.4:
                    self.current_frame_face_name_list[k] = self.face_name_known_list[similar_person_num]

                # 矩形框 / Draw rectangle
                for kk, d in enumerate(faces):
                    # 绘制矩形框
                    cv2.rectangle(current_frame, tuple([d.left(), d.top()]), tuple([d.right(), d.bottom()]),
                                  (255, 255, 255), 2)
            self.current_frame_face_cnt = len(faces)
            img_with_name = self.draw_name(current_frame)
        else:
            img_with_name = current_frame
        log_to_show = str(self.current_frame_face_name_list)
        name_list = self.current_frame_face_name_list
        self.current_frame_face_cnt = 0
        self.current_frame_face_feature_list = []
        self.current_frame_face_name_list = []
        self.current_frame_face_name_position_list = []
        return log_to_show, name_list, img_with_name

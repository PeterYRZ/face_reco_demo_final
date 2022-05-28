# 调用百度API完成人脸识别
import json
import math
import os

import requests
import base64


class Face_Apis:
    def __init__(self):
        self.client_id = 'FfPyoqAzmhmUSOITZFL7iU7W'  # ak
        self.client_secret = 'GHbKMGqny18jLaBy3utNGLPyqAiFLDeB'
        self.all_faces_dict = {}

    def __get_access_token(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + self.client_id + '&client_secret=' + self.client_secret
        header = {'Content-Type': 'application/json; charset=UTF-8'}
        response1 = requests.post(url=host, headers=header)  # <class 'requests.models.Response'>
        json1 = response1.json()  # <class 'dict'>
        access_token = json1['access_token']

        return access_token

    @staticmethod
    def __open_pic2base64(pic_path):
        f = open(pic_path, 'rb')
        img = base64.b64encode(f.read()).decode('utf-8')
        return img

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

    def __bd_rec_face(self, current_face_dir, current_face_name):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        params = {"image": self.__open_pic2base64(current_face_dir), "image_type": "BASE64",
                  "face_field": "age,beauty,glasses,gender,race,expression"}
        header = {'Content-Type': 'application/json'}

        access_token = self.__get_access_token()  # '[调用鉴权接口获取的token]'
        request_url = request_url + "?access_token=" + access_token

        request_url = request_url + "?access_token=" + access_token
        response1 = requests.post(url=request_url, data=params, headers=header)
        json1 = response1.json()
        self.all_faces_dict[str(current_face_name.encode('utf-8').decode())] = {
            "性别".encode('utf-8').decode(): json1["result"]["face_list"][0]['gender']['type'],
            "年龄".encode('utf-8').decode(): json1["result"]["face_list"][0]['age'],
            "人种".encode('utf-8').decode(): json1["result"]["face_list"][0]['race']['type'],
            "颜值评分".encode('utf-8').decode(): Face_Apis.score_add(json1["result"]["face_list"][0]['beauty'])}
        # print("性别为", json1["result"]["face_list"][0]['gender']['type'])
        # print("年龄为", json1["result"]["face_list"][0]['age'], '岁')
        # print("人种为", json1["result"]["face_list"][0]['race']['type'])
        # print("颜值评分为", json1["result"]["face_list"][0]['beauty'], '分/100分')
        # print("是否带眼镜", json1["result"]["face_list"][0]['glasses']['type'])
        # print("图片中包含人物表情：", json1["result"]["face_list"][0]['expression']['type'])

    def use_all_faces_api(self):
        self.all_faces_dict = {}
        for names in os.listdir(os.getcwd() + "\\data\\data_faces"):
            self.__bd_rec_face(os.getcwd() + "\\data\\data_faces\\" + names + "\\1.jpg", names)
        try:
            with open(os.getcwd() + "\\data\\faces_info.json", 'w+') as json_file:
                json_file.truncate()
                json.dump(self.all_faces_dict, json_file, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            print("permission error")
            return False

# if __name__ == '__main__':
#
#     client_id = 'FfPyoqAzmhmUSOITZFL7iU7W'  # ak
#     client_secret = 'GHbKMGqny18jLaBy3utNGLPyqAiFLDeB'  # sk
#
#     # 实例1：人脸识别
#     bd_rec_face(client_id, client_secret)

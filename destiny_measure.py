import json
import requests
import re
import datetime
import random
import os

from PyQt5.QtCore import QThread, pyqtSignal

STAR_DICT = ["Aquarius",
             "Pisces",
             "Aries",
             "Taurus",
             "Gemini",
             "Cancer",
             "Leo",
             "Virgo",
             "Libra",
             "Scorpio",
             "Sagittarius",
             "Capricorn"]


class Destiny_Measure_Service(QThread):
    face_json_info = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.json_file_path = os.getcwd() + "\\data\\faces_info.json"
        self.current_year = datetime.datetime.now().year
        self.birth_year = 0
        self.current_url = ""
        self.eight_words = ""
        self.faces_info_json = {}
        self.destiny_result = {}
        self.face_data = {}

    def run(self):
        self.__update_json_file()
        # self.__read_json_file()
        self.face_json_info.emit(self.faces_info_json)
        print("destiny measurement completed")
        print(self.faces_info_json)

    def __set_face_image_age(self, face_image_age: int):
        self.__update_current_year()
        self.birth_year = self.current_year - face_image_age

    def __read_exist_json_file(self):
        try:
            with open(self.json_file_path, 'r') as faces_json:
                self.faces_info_json = json.load(faces_json)
            return True
        except FileNotFoundError:
            print("FileNotFoundError")
            return False

    def __update_json_file(self):
        if self.__read_exist_json_file():
            for names in self.faces_info_json.keys():
                self.__update_current_year()
                self.__set_face_image_age(self.faces_info_json[names]["年龄"])
                self.__get_eight_words()
                self.__generate_current_url()
                self.__get_response()
                self.faces_info_json[names]["运势"] = self.destiny_result
                self.destiny_result = {}
        with open(self.json_file_path, 'w') as json_file:
            json_file.truncate()
            json.dump(self.faces_info_json, json_file, indent=4, ensure_ascii=False)

    def __get_eight_words(self):
        tg = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        dz = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        if self.birth_year < 9999:
            if self.birth_year == 2020:
                self.eight_words = tg[6] + dz[0]
            elif self.birth_year > 2020:
                a = self.birth_year - 2020
                self.eight_words = tg[(6 - a) % 10] + dz[(0 + a) % 12]
            else:
                b = 2020 - self.birth_year
                self.eight_words = tg[(b % 10)] + dz[(b % 12)]

    def __generate_current_url(self):
        random_star_index = random.randint(0, 11)
        self.current_url = f"https://www.xzw.com/fortune/{STAR_DICT[random_star_index]}/"

    def __update_current_year(self):
        self.current_year = datetime.datetime.now().year

    def __get_response(self):
        self.destiny_result = {}
        response = requests.get(self.current_url)
        response.encoding = "utf-8"
        content = response.text
        lis = re.findall('<em style=" width:(.*?)px;">', content)
        comprehensive_fortune, love_fortune, career_fortune, wealth_fortune = [str(int(int(i) / 16)) + "星" for i in lis]
        health_index = re.findall('健康指数：</label>(.*?)<', content, re.S)[0]
        negotiation_Index = re.findall('商谈指数：</label>(.*?)<', content, re.S)[0]
        lucky_color = re.findall('幸运颜色：</label>(.*?)<', content, re.S)[0]
        lucky_num = re.findall('幸运数字：</label>(.*?)<', content, re.S)[0]
        match_constellation = re.findall('速配星座：</label>(.*?)<', content, re.S)[0]
        short_comment = re.findall('短评：</label>(.*?)<', content, re.S)[0]
        detail_comprehensive_fortune = re.findall('综合运势</strong><span>(.*?)</span>', content, re.S)[0]
        detail_love_fortune = re.findall('爱情运势</strong><span>(.*?)</span>', content, re.S)[0]
        detail_career = re.findall('事业学业</strong><span>(.*?)</span>', content, re.S)[0]
        detail_wealth = re.findall('财富运势</strong><span>(.*?)</span>', content, re.S)[0]
        detail_wealth_fortune = re.findall('健康运势</strong><span>(.*?)</span>', content, re.S)[0]
        self.destiny_result[
            "今日运势总览"] = "综合运势:", comprehensive_fortune, "爱情运势:", love_fortune, "事业运势:", career_fortune, "健康运势:", wealth_fortune
        self.destiny_result["健康指数"] = health_index
        self.destiny_result["商谈指数"] = negotiation_Index
        self.destiny_result["幸运颜色"] = lucky_color
        self.destiny_result["幸运数字"] = lucky_num
        self.destiny_result["速配星座"] = match_constellation
        self.destiny_result["短评"] = short_comment
        self.destiny_result["综合运势"] = detail_comprehensive_fortune
        self.destiny_result["爱情运势"] = detail_love_fortune
        self.destiny_result["事业学业"] = detail_career
        self.destiny_result["财富运势"] = detail_wealth
        self.destiny_result["健康运势"] = detail_wealth_fortune

    def __read_json_file(self):
        with open(os.getcwd() + "\\data\\faces_info.json", 'r') as json_file:
            self.face_data = json.load(json_file)

# 人脸识别身份认证系统

#### 介绍

 **如果本项目帮助到了您，请您点亮Star支持我，谢谢** 

在“信息系统与安全对抗技术”上作为结课代码提交的文件，现开源于此，供大家参考。本项目采用Python语言开发，在跨年龄识别功能中引用了Paddle模块，对除跨年龄识别模块的部分进行了Windows安装包打包。项目中仍有诸多缺陷，请大家有何需求和建议请在issue中讨论，时间和能力允许范围内我会予以解答和完善。

#### 软件架构
软件架构说明
##### 系统结构图
![输入图片说明](readme/img2%E7%B3%BB%E7%BB%9F%E7%BB%93%E6%9E%84%E5%9B%BE.png)

##### 人脸检测接口图
![输入图片说明](readme/img3%E4%BA%BA%E8%84%B8%E6%A3%80%E6%B5%8B%E6%8E%A5%E5%8F%A3.png)
##### 数据处理接口图
![输入图片说明](readme/img4%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86%E6%8E%A5%E5%8F%A3.png)
##### 人脸识别接口图
![输入图片说明](readme/img5%E4%BA%BA%E8%84%B8%E8%AF%86%E5%88%AB%E6%8E%A5%E5%8F%A3.png)

#### 安装教程

##### 体验本项目成果请从release页面下载
Release:
[Windows Release V1.0-beta](https://gitee.com/youhuangforest/face_reco_demo_final/releases/v1.0-beta)
百度网盘：
[Windows Release V1.0-beta 百度网盘链接 提取码：0d6s](链接：https://pan.baidu.com/s/1HohFDzmu3LVf_yJHeAFAig)https://pan.baidu.com/s/1HohFDzmu3LVf_yJHeAFAig

##### 使用源码运行的用户请按照以下方式操作

1.  推荐Windows环境下使用PyCharm打开Master文件夹
2.  本项目使用Python3.9编写，安装requirements.txt中的文件，使用命令

```
pip install -r requirements.txt
```

3.  请下载[shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)和[dlib_face_recognition_resnet_model_v1](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2)，解压到本项目data\data_dlib中，然后分别复制一份，重命名为“dlib_face_recognition_resnet_model_v1_reco.dat”和“shape_predictor_68_face_landmarks_reco.dat”，你可以在代码中看到四个名字
4.  请下载[ppgan](https://gitee.com/paddlepaddle/PaddleGAN/tree/develop/ppgan)中的文件（apps，datasets，engins，__init__.py，version.py等全部文件），装入paddle_gan\ppgan文件夹中，保证引用"from paddle_gan.ppgan.apps import *"等语句不会出现问题
5.  运行ui_main.py或添加运行ui_main.py的运行配置，不需要输入参数
6.  若运行出现错误，且错误为缺少安装包，请自行 pip install 对应的包名。

#### 使用说明

1.  详细使用说明按需在后续更新本README文件，本项目的图形用户界面比较清晰，各控件功能请选中对应方法，按住Ctrl键追踪，追踪到多线程模块即可

#### 参与贡献

本项目代码由余任之编写，余任之持有本仓库。余任之、肖仲煜参与本项目的构建。部分功能使用了Paddle框架。
联系方式：peterrolls@qq.com


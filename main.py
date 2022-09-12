import os
import cv2
import numpy as np

RESOLUTIONS = {
	"4k": (3840, 2160),
	"2k": (2560, 1440),
	"1080p": (1920, 1080),
	"720p": (1280, 720),
	"360p": (640, 360)
}

COLORS = {
	"black": (0, 0, 0),
	"white": (255, 255, 255)
}


def pic_completion(in_pic: np.ndarray, target: tuple, color: tuple) -> np.ndarray:
	width, length = in_pic.shape[:2]
	full_width, full_length = target
	front = (full_width - width) // 2
	back = full_width - width - front
	left = (full_length - length) // 2
	right = full_length - length - left
	return cv2.copyMakeBorder(in_pic, front, back, left, right, cv2.BORDER_CONSTANT, value=color)


def pic_read_trans(file_path, size="4k", background="white") -> np.ndarray:
	# 处理目标分辨率
	if type(size) == tuple and len(size) == 2:
		resolution = size
	elif type(size) == str and (size.lower() in RESOLUTIONS):
		resolution = RESOLUTIONS[size.lower()]
	else:
		resolution = RESOLUTIONS["1080p"]
	resolution: tuple = (resolution[1], resolution[0])
	
	# 处理底色
	if type(background) == tuple and len(background) == 3:
		color: tuple = background
	elif type(background) == str and (background.lower() in COLORS):
		color: tuple = COLORS[background.lower()]
	else:
		color: tuple = COLORS["white"]
	
	# 将图片读为ndarray并缩放到分辨率内
	cv_img: np.ndarray = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
	pic_length, pic_width = cv_img.shape[1], cv_img.shape[0]
	if pic_length / pic_width > 16 / 9:
		pic_width = int(pic_width * int(resolution[1] * 0.9) / pic_length)
		pic_length = int(resolution[1] * 0.9)
	else:
		pic_length = int(pic_length * int(resolution[0]) / pic_width)
		pic_width = int(resolution[0])
	cv_img = cv2.resize(cv_img, (pic_length, pic_width))
	cv_img = pic_completion(cv_img, resolution, color)
	return cv_img


def pic_walk(in_cd: str):
	res = []
	for root, dirs, files in os.walk(in_cd):
		for file in files:
			if file.split(".")[-1] in ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]:
				res.append(file)
	print(f"文件读入完成，共{len(res)}张图片")
	return res


if __name__ == '__main__':
	# 标准输入
	cd = input("请输入照片文件夹：")
	while not os.path.exists(cd):
		cd = input("文件夹不存在，请重新输入：")
	
	try:
		sec = eval(input("请输入每张图片显示的秒数："))
	except NameError and SyntaxError:
		sec = 2
	
	try:
		rate = eval(input("请输入帧率："))
	except NameError and SyntaxError:
		rate = 30
	
	in_size = input("请输入视频清晰度：")
	if ("," in in_size) and len(in_size.split(",")) == 2:
		in_size = in_size.split()
		in_size[0], in_size[1] = eval(in_size[0]), eval(in_size[1])
		in_size = tuple(in_size)
	elif in_size in RESOLUTIONS:
		in_size = RESOLUTIONS[in_size]
	else:
		in_size = RESOLUTIONS["1080p"]
	
	in_background = input("请输入视频背景颜色：")
	if ("," in in_background) and len(in_background.split(",")) == 3:
		in_background = in_background.split()
		in_background[0], in_background[1], in_background[2] = \
			eval(in_background[0]), eval(in_background[1]), eval(in_background[2])
		in_background = tuple(in_background)
	elif in_background in COLORS:
		in_background = COLORS[in_background]
	else:
		in_background = COLORS["white"]
	in_background = in_background[::-1]
	
	song = input("请输入bgm音频文件地址：")
	while not os.path.isfile(song):
		song = input("文件不存在，请重新输入：")
	
	# 视频初始化
	video = cv2.VideoWriter(cd + "/" + "full_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), rate, in_size)
	
	# 照片资源读写
	count = 0
	for pic in pic_walk(cd):
		img = pic_read_trans(cd + "/" + pic, size=in_size, background=in_background)
		for _ in range(int(rate * sec)):
			video.write(img)
		print(pic + "转换完成!")
		count += 1
	
	video.release()
	
	os.system("ffmpeg -i " + cd + "/" + "full_video.mp4" + " -i " + song + " out.mp4")

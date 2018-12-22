import requests
import shutil
from datetime import datetime
from pytesseract import *
from PIL import Image
from queue import Queue
import cv2
import os
from fnmatch import fnmatch


def clear_border(img, img_name):
    """
    去除边框
    """
    filename = './out_img/' + img_name.split('.')[0] + '-clearBorder.jpg'
    h, w = img.shape[:2]
    for y in range(0, w):
        for x in range(0, h):
            # if y ==0 or y == w -1 or y == w - 2:
            if y < 2 or y > w - 2:
                img[x, y] = 255
            # if x == 0 or x == h - 1 or x == h - 2:
            if x < 2 or x > h - 2:
                img[x, y] = 255
    cv2.imwrite(filename, img)
    return img


def interference_line(img, img_name):
    """
    干扰线降噪
    """
    filename = './out_img/' + img_name.split('.')[0] + '-interferenceline.jpg'
    h, w = img.shape[:2]
    # ！！！opencv矩阵点是反的
    # img[1,2] 1:图片的高度，2：图片的宽度
    for y in range(1, w - 1):
        for x in range(1, h - 1):
            count = 0
            if img[x, y - 1] > 245:
                count = count + 1
            if img[x, y + 1] > 245:
                count = count + 1
            if img[x - 1, y] > 245:
                count = count + 1
            if img[x + 1, y] > 245:
                count = count + 1
            if count > 2:
                img[x, y] = 255
    cv2.imwrite(filename, img)
    return img


def interference_point(img, img_name, x=0, y=0):
    """
    点降噪
    9邻域框,以当前点为中心的田字框,黑点个数
    :param x:
    :param y:
    :return:
    """
    filename =  './out_img/' + img_name.split('.')[0] + '-interferencePoint.jpg'
    # todo 判断图片的长宽度下限, 当前像素点的值
    cur_pixel = img[x, y]
    height,width = img.shape[:2]

    for y in range(0, width - 1):
        for x in range(0, height - 1):
            if y == 0:  # 第一行
                if x == 0:  # 左上顶点,4邻域
                    # 中心点旁边3个点
                    sum = int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x + 1, y]) \
                          + int(img[x + 1, y + 1])
                    if sum <= 2 * 245:
                        img[x, y] = 0
                elif x == height - 1:  # 右上顶点
                    sum = int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x - 1, y]) \
                          + int(img[x - 1, y + 1])
                    if sum <= 2 * 245:
                        img[x, y] = 0
                else:  # 最上非顶点,6邻域
                    sum = int(img[x - 1, y]) \
                          + int(img[x - 1, y + 1]) \
                          + int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x + 1, y]) \
                          + int(img[x + 1, y + 1])
                    if sum <= 3 * 245:
                        img[x, y] = 0
            elif y == width - 1:  # 最下面一行
                if x == 0:  # 左下顶点
                    # 中心点旁边3个点
                    sum = int(cur_pixel) \
                          + int(img[x + 1, y]) \
                          + int(img[x + 1, y - 1]) \
                          + int(img[x, y - 1])
                    if sum <= 2 * 245:
                        img[x, y] = 0
                elif x == height - 1:  # 右下顶点
                    sum = int(cur_pixel) \
                          + int(img[x, y - 1]) \
                          + int(img[x - 1, y]) \
                          + int(img[x - 1, y - 1])

                    if sum <= 2 * 245:
                        img[x, y] = 0
                else:  # 最下非顶点,6邻域
                    sum = int(cur_pixel) \
                          + int(img[x - 1, y]) \
                          + int(img[x + 1, y]) \
                          + int(img[x, y - 1]) \
                          + int(img[x - 1, y - 1]) \
                          + int(img[x + 1, y - 1])
                    if sum <= 3 * 245:
                        img[x, y] = 0
            else:  # y不在边界
                if x == 0:  # 左边非顶点
                    sum = int(img[x, y - 1]) \
                          + int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x + 1, y - 1]) \
                          + int(img[x + 1, y]) \
                          + int(img[x + 1, y + 1])

                    if sum <= 3 * 245:
                        img[x, y] = 0
                elif x == height - 1:  # 右边非顶点
                    sum = int(img[x, y - 1]) \
                          + int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x - 1, y - 1]) \
                          + int(img[x - 1, y]) \
                          + int(img[x - 1, y + 1])

                    if sum <= 3 * 245:
                        img[x, y] = 0
                else:  # 具备9领域条件的
                    sum = int(img[x - 1, y - 1]) \
                          + int(img[x - 1, y]) \
                          + int(img[x - 1, y + 1]) \
                          + int(img[x, y - 1]) \
                          + int(cur_pixel) \
                          + int(img[x, y + 1]) \
                          + int(img[x + 1, y - 1]) \
                          + int(img[x + 1, y]) \
                          + int(img[x + 1, y + 1])
                    if sum <= 4 * 245:
                        img[x, y] = 0
    cv2.imwrite(filename, img)
    return img


def _get_dynamic_binary_image(im, filedir, img_name):
    """
    自适应阀值二值化
    :param filedir:
    :param img_name:
    :return:
    """
    filename = './out_img/' + img_name.split('.')[0] + '-binary.jpg'
    print('binary_image', filename)
    img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    th1 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
    cv2.imwrite(filename, th1)
    return th1


def _get_static_binary_image(img_file, threshold=140):
    """
    手动二值化
    """
    img = Image.open(img_file)
    img = img.convert('L')
    pixdata = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    return img


def cfs(im, x_fd, y_fd):
    """
    用队列和集合记录遍历过的像素坐标代替单纯递归以解决cfs访问过深问题
    :param im:
    :param x_fd:
    :param y_fd:
    :return:
    """
    # print('**********')
    xaxis = []
    yaxis = []
    visited = set()
    q = Queue()
    q.put((x_fd, y_fd))
    visited.add((x_fd, y_fd))
    # 四邻域
    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    while not q.empty():
        x, y = q.get()
        for xoffset, yoffset in offsets:
            x_neighbor, y_neighbor = x+xoffset, y+yoffset
            if (x_neighbor, y_neighbor) in visited:
                # 已经访问过了
                continue
            visited.add((x_neighbor, y_neighbor))
            try:
                if im[x_neighbor, y_neighbor] == 0:
                    xaxis.append(x_neighbor)
                    yaxis.append(y_neighbor)
                    q.put((x_neighbor, y_neighbor))
            except IndexError:
                pass
    # print(xaxis)
    if len(xaxis) == 0 or len(yaxis) == 0:
        xmax = x_fd + 1
        xmin = x_fd
        ymax = y_fd + 1
        ymin = y_fd
    else:
        xmax = max(xaxis)
        xmin = min(xaxis)
        ymax = max(yaxis)
        ymin = min(yaxis)
        #ymin,ymax=sort(yaxis)
    return ymax, ymin, xmax, xmin


def detectFgPix(im,xmax):
    '''搜索区块起点'''
    h, w = im.shape[:2]
    for y_fd in range(xmax+1, w):
        for x_fd in range(h):
            if im[x_fd, y_fd] == 0:
                return x_fd, y_fd


def CFS(im):
    '''切割字符位置'''
    # 各区块长度L列表
    zoneL = []
    # 各区块的X轴[起始，终点]列表
    zoneWB = []
    # 各区块的Y轴[起始，终点]列表
    zoneHB = []
    # 上一区块结束黑点横坐标,这里是初始化
    xmax = 0
    for i in range(10):
        try:
            x_fd, y_fd = detectFgPix(im,xmax)
            # print(y_fd,x_fd)
            xmax, xmin, ymax, ymin = cfs(im, x_fd, y_fd)
            L = xmax - xmin
            H = ymax - ymin
            zoneL.append(L)
            zoneWB.append([xmin,xmax])
            zoneHB.append([ymin,ymax])
        except TypeError:
            return zoneL,zoneWB,zoneHB
    return zoneL,zoneWB,zoneHB


def cutting_img(im, im_position, img,xoffset = 1, yoffset = 1):
    filename =  './out_img/' + img.split('.')[0]
    # 识别出的字符个数
    im_number = len(im_position[1])
    # 切割字符
    for i in range(im_number):
        im_start_X = im_position[1][i][0] - xoffset
        im_end_X = im_position[1][i][1] + xoffset
        im_start_Y = im_position[2][i][0] - yoffset
        im_end_Y = im_position[2][i][1] + yoffset
        cropped = im[im_start_Y:im_end_Y, im_start_X:im_end_X]
        cv2.imwrite(filename + '-cutting-' + str(i) + '.jpg', cropped)


def save_image_from_url(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb+') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


if __name__ == "__main__":

    now = int(datetime.utcnow().timestamp())

    image_file = "./" + str(now) + '.jpg'

    img_name = str(now) + '.jpg'

    save_image_from_url("https://www.gconline.cn/authImg", image_file)

    # 去除边框
    im = cv2.imread(image_file)
    print('直接识别', image_to_string(im))

    im = clear_border(im, img_name)
    print('去除边框识别', image_to_string(im))

    image_file = './out_img/' + str(now) + '-clearBorder.jpg'

    # im = _get_static_binary_image(image_file, threshold=10)
    # print('二值化识别10', image_to_string(im))
    #
    # im = _get_static_binary_image(image_file, threshold=50)
    # print('二值化识别50', image_to_string(im))

    im = _get_static_binary_image(image_file, threshold=125)
    print('二值化识别125', image_to_string(im))

    im = _get_static_binary_image(image_file, threshold=135)
    print('二值化识别135', image_to_string(im))

    # im = _get_static_binary_image(image_file, threshold=200)
    # print('二值化识别200', image_to_string(im))
    #
    # im = _get_static_binary_image(image_file, threshold=250)
    # print('二值化识别250', image_to_string(im))

    # 自适应阈值二值化
    im = cv2.imread(image_file)
    im = _get_dynamic_binary_image(im, ".", img_name)

    # 对图片进行干扰线降噪
    im = interference_line(im, img_name)

    # 对图片进行点降噪
    im = interference_point(im, img_name)
    print('降噪识别', image_to_string(im))

    # 切割的位置
    im_position = CFS(im)

    maxL = max(im_position[0])
    minL = min(im_position[0])

    # 如果有粘连字符，如果一个字符的长度过长就认为是粘连字符，并从中间进行切割
    if maxL > minL + minL * 0.7:
        maxL_index = im_position[0].index(maxL)
        minL_index = im_position[0].index(minL)
        # 设置字符的宽度
        im_position[0][maxL_index] = maxL // 2
        im_position[0].insert(maxL_index + 1, maxL // 2)
        # 设置字符X轴[起始，终点]位置
        im_position[1][maxL_index][1] = im_position[1][maxL_index][0] + maxL // 2
        im_position[1].insert(maxL_index + 1, [im_position[1][maxL_index][1] + 1, im_position[1][maxL_index][1] + 1 + maxL // 2])
        # 设置字符的Y轴[起始，终点]位置
        im_position[2].insert(maxL_index + 1, im_position[2][maxL_index])

    # 切割字符，要想切得好就得配置参数，通常 1 or 2 就可以
    cutting_img(im, im_position, img_name,1,1)

    # 识别验证码
    cutting_img_num = 0
    for file in os.listdir('./out_img'):
        str_img = ''
        if fnmatch(file, '%s-cutting-*.jpg' % img_name.split('.')[0]):
            cutting_img_num += 1
    for i in range(cutting_img_num):
        try:
            file = './out_img/%s-cutting-%s.jpg' % (img_name.split('.')[0], i)
            # 识别验证码  单个字符是10，一行文本是7
            str_img = str_img + image_to_string(Image.open(file), lang = 'eng', config='-psm 10')
        except Exception as err:
            pass
    print('切图：%s' % cutting_img_num)
    print('识别为：%s' % str_img)

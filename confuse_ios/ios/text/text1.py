

import cv2
import os
from PIL import Image

def handle():
    # 加载图像
    img = cv2.imread('icon_test.png')
    # 获取图像尺寸
    height, width = img.shape[:2]
    # 遍历每个像素点
    for i in range(height):
        for j in range(width):
            # 获取像素值
            pixel = img[i, j]
            print(pixel)
            # 修改像素值
            img[i, j] = (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])
            # 显示修改后的图像
            cv2.imshow('image', img)
            cv2.waitKey()
            cv2.destroyAllWindows()

def handle2():
    img = Image.open('icon_test.png')
    print(img.size)
    width = img.size[0]
    height = img.size[1]
    for i in range(0,width):
        for j in range(0,height):
            data = (img.getpixel((i,j)))
            # print(str(data))
            r = data[0] + 2
            g = data[1] + 2
            b = data[2] + 2
            if r > 255: r = 255
            if g > 255: g = 255
            if b > 255: b = 255
            img.putpixel((i,j),(r,g,b,data[3]))
    
    img = img.convert('RGBA')
    img.save('icon_test_handle2.png')



if __name__ == '__main__':
    handle2()
    pass
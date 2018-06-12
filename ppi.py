
#-*- coding: utf-8 -*- # 한글 주석쓰려면 이거 해야함
import cv2  # opencv 사용
import numpy as np

def grayscale(img):  # 흑백이미지로 변환
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def canny(img, low_threshold, high_threshold):  # Canny 알고리즘
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_blur(img, kernel_size):  # 가우시안 필터
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def region_of_interest(img, vertices, color3=(255, 255, 255), color1=255):  # ROI 셋팅
    global mask
    mask = np.zeros_like(img)  # mask = img와 같은 크기의 빈 이미지

    if len(img.shape) > 2:  # Color 이미지(3채널)라면 :
        color = color3
    else:  # 흑백 이미지(1채널)라면 :
        color = color1

    # vertices에 정한 점들로 이뤄진 다각형부분(ROI 설정부분)을 color로 채움
    cv2.fillPoly(mask, vertices, color)

    # 이미지와 color로 채워진 ROI를 합침
    ROI_image = cv2.bitwise_and(img, mask)
    return ROI_image

def hough_lines(ROI_img, t):
    lines_data = cv2.HoughLines(ROI_img,1,np.pi/180,t)
    
    pt1_x=0
    pt1_y=0
    pt2_x=0
    pt2_y=0
    pt3_x=0
    pt3_y=0
    pt4_x=0
    pt4_y=0
    leftP1_x=0
    leftP1_y=0
    leftP2_x=500
    leftP2_y=0
    rightP1_x=500
    rightP1_y=0
    rightP2_x=0
    rightP2_y=0
    
    if lines_data is not None:
        
        #left_lines = []
        #right_lines = []
        length = 800
        tag = 0
        
        line_num = len(lines_data)
        
        if line_num > 1 :
            lines_data = np.squeeze(lines_data)
            
            for rho, theta in lines_data:
                if (tag != 0):
                    pt1_x=0
                    pt1_y=0
                    pt2_x=0
                    pt2_y=0
                    pt3_x=0
                    pt3_y=0
                    pt4_x=0
                    pt4_y=0
                    leftP1_x=0
                    leftP1_y=0
                    leftP2_x=500
                    leftP2_y=0
                    rightP1_x=500
                    rightP1_y=0
                    rightP2_x=0
                    rightP2_y=0
                
                if (theta < 1.41) and (theta >= 0):
                    #left_lines.append([theta,rho])
                    a1 = np.cos(theta)
                    b1 = np.sin(theta)
                    x0 = a1*rho
                    y0 = b1*rho
                    pt1_x=int(x0 + length*(-b1))
                    pt1_y=int(y0 + length*(a1))
                    pt2_x=int(x0 - length*(-b1))
                    pt2_y=int(y0 - length*(a1))
                    tag = 0
                    
                elif (theta < 3.14) and (theta >= 1.77):
                    #right_lines.append([theta,rho])
                    a2 = np.cos(theta)
                    b2 = np.sin(theta)
                    x0 = a2*rho
                    y0 = b2*rho
                    pt3_x=int(x0 + length*(-b2))
                    pt3_y=int(y0 + length*(a2))
                    pt4_x=int(x0 - length*(-b2))
                    pt4_y=int(y0 - length*(a2))
                    tag = 0
                    
            if (pt1_x != 0) and (pt3_x != 0):
                gradientL = (pt2_y - pt1_y) / (pt2_x - pt1_x)
                interceptL = pt2_y - gradientL * pt2_x
                gradientR = (pt4_y - pt3_y) / (pt4_x - pt3_x)
                interceptR = pt4_y - gradientR * pt4_x
                
                banishP_x = int((interceptR - interceptL) / (gradientL - gradientR))
                banishP_y = int(gradientL * banishP_x + interceptL)
                
                bb1 = pt2_y - gradientL * pt2_x;
                leftP2_y = height;
                leftP2_x = (leftP2_y - bb1) / gradientL;

                bb2 = pt3_y - gradientR * pt3_x;
                rightP2_y = height;
                rightP2_x = (rightP2_y - bb2) / gradientR;
                
                cv2.line(image,(pt1_x,pt1_y),(banishP_x,banishP_y),(255,0,0),2)
                cv2.line(image,(banishP_x,banishP_y),(pt4_x,pt4_y),(0,0,255),2)
                
                
                print("**********Both Line Detect************")
                print("banishP_x : %d, banishP_y : %d" %(banishP_x, banishP_y))
                print("leftP1_x  : %d, rightP1_x : %d" %(leftP1_x, rightP1_x))
                print("leftP2_x  : %d, rightP2_x : %d" %(leftP2_x, rightP2_x))
                      
                tag = 1
            elif (pt1_x != 0) and (pt3_x == 0):
                # left Point detection 

                # leftLine : first linear equation
                gradientL = (pt2_y - pt1_y) / (pt2_x - pt1_x)		# gradient
                interceptL = pt2_y - gradientL * pt2_x;					# y-intercept

                # leftPoint : nodePoint of two equation
                leftP1_x = (int)(interceptL / -gradientL)
                leftP1_y = (int)(gradientL * leftP1_x + interceptL)

                bb1 = leftP1_y - gradientL * leftP1_x
                leftP2_y = height
                leftP2_x = (leftP2_y - bb1) / gradientL
                
                cv2.line(image,(leftP1_x,leftP1_y),(pt1_x,pt1_y),(255,0,0),2)
                print("**********Left Line Detect************")
                print("leftP1_x  : %d, leftP1_y : %d" %(leftP1_x, leftP1_y))
                print("leftP2_x  : %d, leftP2_y : %d" %(leftP2_x, leftP2_y))
                tag = 2
                
            elif (pt1_x == 0) and (pt3_x != 0):
                gradientR = (pt4_y - pt3_y) / (pt4_x - pt3_x);		# gradient
                interceptR = pt4_y - gradientR * pt4_x;							# y-intercept

			# rightPoint : nodePoint of two equation
                rightP1_x = (int)(interceptR / -gradientR)
                rightP1_y = (int)(gradientR * rightP1_x + interceptR)

                bb2 = rightP1_y - gradientR * rightP1_x
                rightP2_y = height
                rightP2_x = (rightP2_y - bb2) / gradientR
                
                cv2.line(image,(pt4_x,pt4_y),(rightP1_x,rightP1_y),(0,0,255),2)
                print("**********Right Line Detect************")
                print("rightP1_x  : %d, rightP1_y : %d" %(rightP1_x, rightP1_y))
                print("rightP2_x  : %d, rightP2_y : %d" %(rightP2_x, rightP2_y))
                tag = 3
        else:
            print("fuck")

cap = cv2.VideoCapture(0)  # 동영상 불러오기
cap.set(3, 320)
cap.set(4, 240)

while (cap.isOpened()):
    ret, image = cap.read()

    height, width = image.shape[:2]  # 이미지 높이, 너비
    
    #width = 320
    #height = 240
    
    gray_img = grayscale(image)  # 흑백이미지로 변환

    blur_img = gaussian_blur(gray_img, 3)  # Blur 효과

    canny_img = canny(blur_img, 70, 210)  # Canny edge 알고리즘

    vertices = np.array(
        [[(-100, height), (width / 8, height / 3), (width * 7 / 8, height / 3), (width+100, height)]],
        dtype=np.int32)
    ROI_img = region_of_interest(canny_img, vertices)  # ROI 설정

    Hough_img = hough_lines(ROI_img, 100)

    cv2.imshow('image',image)
    cv2.imshow('edge',ROI_img)
    
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()



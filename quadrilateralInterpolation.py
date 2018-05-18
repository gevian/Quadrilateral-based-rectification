__author__ = 'Magnus Heitzler'

import cv2
import numpy as np


def rectify(img, px, py, width, height):
    A=np.matrix("[1 0 0 0; 1 1 0 0; 1 1 1 1; 1 0 1 0]")

    AI = np.linalg.inv(A)
    a = np.dot(AI, py.T)
    b = np.dot(AI, px.T)

    rectifiedImg = np.zeros([height, width, 3],dtype=np.uint8)

    vstride = 1/height
    hstride = 1/width


    for y in np.arange(0, 1, vstride):
        print(y)
        m = 1 - y
        for x in np.arange(0, 1, hstride):
            l = x

            lm = l*m

            # method 1: seems to be a bit faster
            y_img = a[0,0] + a[0,1]*l + a[0,2]*m + a[0,3]*lm
            x_img = b[0,0] + b[0,1]*l + b[0,2]*m + b[0,3]*lm

            # method 2
            #parameters = np.asarray([[1, l, m, l*m]]).T
            #y_img = np.dot(a, parameters)[0, 0]
            #x_img = np.dot(b, parameters)[0, 0]

            # nearest neighbor
            #mapValue = img[int(round(y_img)),int(round(x_img))]

            
            # linear interpolation
            ul = img[int(y_img), int(x_img)]
            ur = img[int(y_img), int(x_img + 0.5)]
            lr = img[int(y_img + 0.5), int(x_img + 0.5)]
            ll = img[int(y_img + 0.5), int(x_img)]
            
            upperWeight = 1 - (y_img - int(y_img))
            leftWeight  = 1 - (x_img - int(x_img))
            lowerWeight = upperWeight
            rightWeight = leftWeight
            
            mapValue = upperWeight * leftWeight * ul + upperWeight * rightWeight * ur + lowerWeight * rightWeight * lr + lowerWeight * leftWeight * ll
            
            rectifiedImg[int(round(y * height)), int(round(x * width))] = mapValue


    return rectifiedImg


def rectifyVectorizedBilinear(img, px, py, width, height):
    A=np.matrix("[1 0 0 0; 1 1 0 0; 1 1 1 1; 1 0 1 0]")

    AI = np.linalg.inv(A)
    a = np.dot(AI, py.T)
    b = np.dot(AI, px.T)

    vstride = 1/height
    hstride = 1/width

    vIndices = 1 - np.arange(0, 1, vstride)
    hIndices = np.arange(0, 1, hstride)

    m = np.zeros([height, width],dtype=np.float32)
    m.T[:,:] = vIndices

    l = np.zeros([height, width],dtype=np.float32)
    l[:,:] = hIndices

    ml = m*l

    a0 = np.full([height, width], a[0,0], dtype=np.float32)
    a1 = np.full([height, width], a[0,1], dtype=np.float32)
    a2 = np.full([height, width], a[0,2], dtype=np.float32)
    a3 = np.full([height, width], a[0,3], dtype=np.float32)

    y_img = (a0 + a1 * l + a2 * m + a3 * ml)
    y_img_reshaped = y_img.reshape(height * width)
    
    b0 = np.full([height, width], b[0,0], dtype=np.float32)
    b1 = np.full([height, width], b[0,1], dtype=np.float32)
    b2 = np.full([height, width], b[0,2], dtype=np.float32)
    b3 = np.full([height, width], b[0,3], dtype=np.float32)

    x_img = (b0 + b1 * l + b2 * m + b3 * ml)
    x_img_reshaped = x_img.reshape(height * width)

    left_img   = np.floor(x_img_reshaped).astype(int)
    right_img  = np.ceil(x_img_reshaped).astype(int)
    top_img    = np.ceil(y_img_reshaped).astype(int)
    bottom_img = np.floor(y_img_reshaped).astype(int)

    tl = img[top_img, left_img]
    tr = img[top_img, right_img]
    bl = img[bottom_img, left_img]
    br = img[bottom_img, right_img]    

    lw  = x_img_reshaped - left_img
    rw  = 1 - lw
    tw  = top_img - y_img_reshaped
    bw  = 1 - tw
        
    tlw = np.asarray([(bw * rw)]).T
    trw = np.asarray([(bw * lw)]).T
    blw = np.asarray([(tw * rw)]).T
    brw = np.asarray([(tw * lw)]).T
    
    imgValues = tlw * tl + trw * tr + blw * bl + brw * br

    rectifiedImg = imgValues.reshape((height, width, 3))


    return rectifiedImg
    
    
    
def rectifyVectorized(img, px, py, width, height):
    A=np.matrix("[1 0 0 0; 1 1 0 0; 1 1 1 1; 1 0 1 0]")

    AI = np.linalg.inv(A)
    a = np.dot(AI, py.T)
    b = np.dot(AI, px.T)

    vstride = 1/height
    hstride = 1/width

    vIndices = 1 - np.arange(0, 1, vstride)
    hIndices = np.arange(0, 1, hstride)

    m = np.zeros([height, width],dtype=np.float32)
    m.T[:,:] = vIndices

    l = np.zeros([height, width],dtype=np.float32)
    l[:,:] = hIndices

    ml = m*l

    a0 = np.full([height, width], a[0,0], dtype=np.float32)
    a1 = np.full([height, width], a[0,1], dtype=np.float32)
    a2 = np.full([height, width], a[0,2], dtype=np.float32)
    a3 = np.full([height, width], a[0,3], dtype=np.float32)

    y_img = np.rint(a0 + a1 * l + a2 * m + a3 * ml).astype(int)

    b0 = np.full([height, width], b[0,0], dtype=np.float32)
    b1 = np.full([height, width], b[0,1], dtype=np.float32)
    b2 = np.full([height, width], b[0,2], dtype=np.float32)
    b3 = np.full([height, width], b[0,3], dtype=np.float32)

    x_img = np.rint(b0 + b1 * l + b2 * m + b3 * ml).astype(int)

    y_img_reshaped = y_img.reshape(height * width)
    x_img_reshaped = x_img.reshape(height * width)

    imgValues = img[y_img_reshaped, x_img_reshaped]

    rectifiedImg = imgValues.reshape((height, width, 3))


    return rectifiedImg
    
    

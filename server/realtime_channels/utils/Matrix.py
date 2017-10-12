import numpy as np

#http://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib/
class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Matrix4x4:
    matrix = 0

    def __init__(self):
        self.matrix = np.zeros((4, 4))

    def setRows(self, row, col1, col2, col3, col4):
        self.matrix[row][0] = col1
        self.matrix[row][1] = col2
        self.matrix[row][2] = col3
        self.matrix[row][3] = col4

class MatOfPoint3D:
    matrix = 0

    def __init__(self, point1, point2, point3, point4, point5, point6, point7):
        self.matrix[0] = point1 #left eyes
        self.matrix[1] = point2 #right eyes
        self.matrix[2] = point3 #nose
        self.matrix[3] = point4 #left mouth
        self.matrix[4] = point5 #right mouth
        self.matrix[5] = point6 #left ear
        self.matrix[6] = point7 #right ear
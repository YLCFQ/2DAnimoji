from __future__ import absolute_import
import json
import logging
import math

from realtime_channels.celery import app
from .models import Job
from channels import Channel
from utils.matrix4x4 import Matrix
import time

#libraries for facial data extraction
import cv2
import numpy as np
import dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('../../shape_predictor_68_face_landmarks.dat')
image_ratio = 0.6

log = logging.getLogger(__name__)

model_points = np.array([
    (-31, 72, 86),  #left eyes
    (31, 72, 86), #right eyes
    (0, 40, 114), #nose
    (-20, 15, 90), #left mouth
    (20, 15, 90), #right mouth
    (-69, 76, -2), #left ear
    (69, 76, -2) #right ear
],dtype="double")

def in_rect(r, p):
    return p[0] > r[0] and p[1] > r[1] and p[0] < r[2] and p[1] < r[3]

def makeFrame(path, img, ptsList, breadthList):
    i = 0
    for pts in ptsList:
        bounds = (0, 0, img.shape[1], img.shape[0])
        subdiv = cv2.Subdiv2D(bounds)
        for p in pts:
            subdiv.insert(p)
        tris = subdiv.getTriangleList()
        for t in tris:
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])

            if in_rect(bounds, pt1) and in_rect(bounds, pt2) and in_rect(bounds, pt3):
                cv2.line(img, pt1, pt2, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0)
                cv2.line(img, pt2, pt3, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0)
                cv2.line(img, pt3, pt1, (0, 255, 0), int(breadthList[i] * 1/100), 8, 0)

def detectFrame(img):
    global detector, predictor, image_ratio
    image = cv2.resize(img, (0,0), fx=image_ratio, fy=image_ratio)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detections = detector(image, 1)

    ptsList = []
    breadthList = []
    for i, d in enumerate(detections):
        shape = predictor(image, d)
        pts = []
        for p in shape.parts():
            if p.x > 0 and p.y > 0:
                pts.append((p.x/image_ratio, p.y/image_ratio))
        ptsList.append(pts)
        breadthList.append(np.sqrt(d.width() ** 2 + d.height() ** 2))
    return ptsList, breadthList

#https://stackoverflow.com/a/42538142
def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def isRotationMatrx(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    print n < 1e-6
    return n < 1e-6

#https://www.learnopencv.com/rotation-matrix-to-euler-angles/
def rotationMatrixToEulerAngels(R):

    assert(isRotationMatrx(R))
    sy = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    print np.array([x, y, z])


def faceAngel(ptsList, size):

    if len(ptsList[0]) != 68:
        return 0
    ptsList = ptsList[0]
    focal_length = size[1]
    center = (size[1]/2, size[0]/2)

    image_points = np.array([
        ((ptsList[38][0] + ptsList[41][0])/2, (ptsList[38][1] + ptsList[41][1])/2), #left eyes
        ((ptsList[43][0] + ptsList[46][0])/2, (ptsList[43][1] + ptsList[46][1]/2)), #right eyes
        (ptsList[33][0], ptsList[33][1]), #nose
        (ptsList[48][0], ptsList[48][1]), #left mouth
        (ptsList[54][0], ptsList[54][1]), #right mouth
        (ptsList[0][0], ptsList[0][1]), #left ear
        (ptsList[16][0], ptsList[16][1]) #right ear
    ], dtype="double")

    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )
    #print "Camera Matrix :\n {0}".format(camera_matrix)




    #print image_points
    #print model_points

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                  dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    #print "Rotation Vector:\n {0}".format(rotation_vector)
    #print "Translation Vector:\n {0}".format(translation_vector)

    rot_mat, _ = cv2.Rodrigues(rotation_vector)

    return translation_vector[0], translation_vector[1]
    #rotationMatrixToEulerAngels(rot_mat)


@app.task
def realTimeFaceProcess(job_id, reply_channel):
    print job_id
    start = time.time()
    job = Job.objects.get(pk=job_id)
    end = time.time()
    print "database latency: " + str(end - start)
    log.debug("Running job_id=%s", job.id)

    img = data_uri_to_cv2_img(job.img)
    size = img.shape

    ptsList, breadthList = detectFrame(img)

    if len(ptsList) == 0:
        ptsList.append([0])
    left_right, top_down = faceAngel(ptsList, size)
    try:
        if len(left_right) == 0:
            left_right.append([0])
    except TypeError:
        pass

    try:
        if len(top_down) == 0:
            top_down.append([0])
    except TypeError:
        pass

    job.status = "completed"
    job.save()

    # Send facial points back to browser client
    if reply_channel is not None:
        Channel(reply_channel).send({
            "text": json.dumps ({
                "action": "completed",
                "id": job.id,
                "img": ptsList,
                "hor": left_right[0],
                "ver": top_down[0]
            })
        })

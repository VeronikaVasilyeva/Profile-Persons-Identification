import math

import cv2
import numpy as np
from facial_landmarks import detect_landmarks


def get_angle(frame, fileName, write=True):
    shape = detect_landmarks(frame)
    if shape is None:
       return []
    landmarks = [shape[33], shape[8], shape[36], shape[45], shape[48], shape[54]]

    imgpts, modelpts, rotate_degree, nose = face_orientation(frame, landmarks)

    cv2.line(frame, tuple(nose), tuple(imgpts[1].ravel()), (0, 0, 255), 1)  
    cv2.line(frame, tuple(nose), tuple(imgpts[0].ravel()), (0, 0, 255), 1)  
    cv2.line(frame, tuple(nose), tuple(imgpts[2].ravel()), (0, 0, 255), 1)  

    for index in range(len(landmarks)):
         #cv2.circle(frame, tuple(modelpts[index].ravel().astype(int)), 2, (0, 255, 0), -1)
         cv2.circle(frame, tuple(landmarks[index]), 2, (255, 255, 0), -1)


    if (write):
        img_path = 'pose' + fileName
        cv2.imwrite(img_path, frame)

    return rotate_degree


def face_orientation(frame, landmarks):
    size = frame.shape  # (height, width, color_channel)

    image_points = np.array([
        (landmarks[0]),  # Nose tip
        (landmarks[1]),  # Chin
        (landmarks[2]),  # Left eye left corner
        (landmarks[3]),  # Right eye right corne
        (landmarks[4]),  # Left Mouth corner
        (landmarks[5])  # Right mouth corner
    ], dtype="double")

    model_points = np.array([
        (0.0, 0.0, 0.0),  # Nose tip
        (0.0, -330.0, -65.0),  # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corne
        (-150.0, -150.0, -125.0),  # Left Mouth corner
        (150.0, -150.0, -125.0)  # Right mouth corner
    ])

    # Camera internals
    center = (size[1] / 2, size[0] / 2)
    focal_length = center[0] / np.tan(60 / 2 * np.pi / 180)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix,
                                                                  dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    axis = np.float32([[500, 0, 0],
                       [0, 500, 0],
                       [0, 0, 500]])

    imgpts, jac = cv2.projectPoints(axis, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
    modelpts, jac2 = cv2.projectPoints(model_points, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
    rvec_matrix = cv2.Rodrigues(rotation_vector)[0]

    proj_matrix = np.hstack((rvec_matrix, translation_vector))
    eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

    pitch, yaw, roll = [math.radians(_) for _ in eulerAngles]

    # pitch = math.degrees(math.asin(math.sin(pitch)))
    # roll = -math.degrees(math.asin(math.sin(roll)))
    yaw_degree = math.degrees(math.asin(math.sin(yaw)))
    norm_angle = sigmoid(10 * (abs(yaw_degree) / 30.0 - 1))

    return imgpts, modelpts, (str(yaw), str(yaw_degree), str(norm_angle)), landmarks[0]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import math

def alignNormalizedPoints(control : list, test: list):
    #index 152 is the bottom of the chin
    #index 10 is top of face
    #index 1 is tip of nose
    #index 168, 6 is middle of eyes
    #etc.
    #pointsOfAlignment = [10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 152]
    #tearducts- 133, 362
    #pointsOfAlignment = [133, 362]

    #top of forehead, bottom of chin - 10, 152
    pointsOfAlignment = [10, 152]
    numPoints = len(pointsOfAlignment)
    delta = 0
    for poa in pointsOfAlignment:
        delta += control[poa] - test[poa]

    delta /= numPoints

    for i in range(len(test)):
        test[i] += delta

    #return control, yCon, test, yTest
    return test

def scalePoints(xCon: list, yCon: list, xTest: list, yTest: list, zCon: list, zTest: list):

    controlDistBetweenEyes = xCon[243] - xCon[362]
    testDistBetweenEyes = xTest[243] - xTest[362]

    scale = controlDistBetweenEyes / testDistBetweenEyes

    scaledXTest = list(map(lambda x: x * scale, xTest))
    scaledYTest = list(map(lambda y: y * scale, yTest))
    scaledZTest = list(map(lambda z: z * scale, zTest))
    
    return scaledXTest, scaledYTest, scaledZTest

def alignNormalizedPointsFixed(xIn : list, yIn: list):
    nostipX = xIn[1]
    nosetipY = yIn[1]

    targetX = .5
    targetY = .5

    deltaX = targetX - nostipX
    deltaY = targetY - nosetipY

    xShift = []
    yShift = []

    for x, y in zip(xIn, yIn):
        xShift.append(x + deltaX)
        yShift.append(y + deltaY) 

    return xShift, yShift


def scalePointsFixed(xIn: list, yIn: list, zIn: list):

    #controlDistBetweenEyes = xCon[243] - xCon[362]
    #hard coding control distance to scale all image to coming from 'same face'
    controlDistBetweenEyes = .05
    testDistBetweenEyes = xIn[243] - xIn[362]

    scale = controlDistBetweenEyes / testDistBetweenEyes

    xOut = list(map(lambda x: x * scale, xIn))
    yOut = list(map(lambda y: y * scale, yIn))
    zOut = list(map(lambda z: z * scale, zIn))
    
    return xOut, yOut, zOut

def flipPoints(input: list):
    flippedPoints = [-p for p in input]
    return flippedPoints

def reversePoints(input: list):
    reveredPoints = [1-p for p in input]
    return reveredPoints

def rotate90CC(affine: np.array):
    rotateMatrix = np.array([[0, 1],
                             [-1, 0]])
    return np.dot(affine, rotateMatrix)

def affineTransform(X: list, Y: list):
    #https://stackoverflow.com/questions/74493141/align-x-and-y-coordinates-of-face-landmarks-in-r
    #133 is left eye tearduct, 362 is right
    #deltaX = X[133] - X[362]
    #deltaY = Y[133] - Y[362]

    #10 is top of forehead, 152 is bottom of chin
    deltaX = X[10] - X[152]
    deltaY = Y[10] - Y[152]
    theta = math.atan2(-deltaY, deltaX)

    rotationMatrix = np.array([[math.cos(theta), -math.sin(theta)],
                              [math.sin(theta), math.cos(theta)]])
    
    rotX = []
    rotY = []

    for x, y in zip(X, Y):
        rotateCoord = np.dot(rotationMatrix, np.array([x, y]))
        rotX.append(rotateCoord[0]) 
        rotY.append(rotateCoord[1])
    
    rotMatrix = np.column_stack((rotX, rotY))

    rotPoints = rotate90CC(rotMatrix)
    rotX = rotPoints[:, 0].tolist()
    rotY = rotPoints[:,1].tolist()

    #rotX = reversePoints(rotX)

    return rotX, rotY

import mediapipe as mp
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import math

def processFrame(xIn: list, yIn: list, zIn: list, frame: int, timeStamp):
    xOut, yOut = affineTransform(xIn, yIn)

    xOut, yOut, zOut = scalePointsFixed(xOut, yOut, zIn)

    xOut, yOut = alignNormalizedPointsFixed(xOut, yOut)

    fig = plt.figure()
    plt.scatter(xOut, yOut, color = 'blue', s = .5)
    plt.title(f'X, Y of Frame : {frame} | {timeStamp}')
    return xOut, yOut, zOut, fig

def create2DFaceArray(xIn: list, yIn: list):
    #assert len(xIn) == 478 and len(yIn) == 478
    face2D = []
    # 1 tip of nose
    # 33, 263 - right and left tips of eyes
    # 199 near bottom of chin
    # 61, 291 - right and left lip crease
    #face must be six points long for matrix multiplication 

    pois = [1, 199, 33, 263, 61, 291]
    for poi in pois:
        face2D.append([xIn[poi], yIn[poi]])
    face2D = np.array(face2D, dtype = np.float64)
    return face2D

def create3DFaceArray(xIn: list, yIn: list, zIn: list):
    #assert len(xIn) == 478 and len(yIn) == 478 and len(zIn) == 478
    face3D = []
    # 1 tip of nose
    # 33, 263 - right and left tips of eyes
    # 199 near bottom of chin
    # 61, 291 - right and left lip crease

    pois = [1, 199, 33, 263, 61, 291]
    for poi in pois:
        face3D.append([xIn[poi], yIn[poi], zIn[poi]])
    face3D = np.array(face3D, dtype = np.float64)
    return face3D

def createModel3DFaceArray():
    modelFace = np.array([
    (0.0, 0.0, 0.0),  # Nose tip
    (0.0, -330.0, -65.0),  # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),  # Right eye right corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0, -150.0, -125.0)   # Right mouth corner
    ])
    return modelFace

def createCamMatrix(imageWidth: int, imageHeight: int):
    focalLength = 1 * imageHeight
    #height, width = im.shape[0], im.shape[1]
    camMatrix = np.array([[focalLength, 0 , imageWidth/2], 
                          [0, focalLength, imageHeight/2],
                          [0, 0, 1]])
    return camMatrix

def scaleLandmarksToImage(xIn: list, yIn: list, zIn: list, imageWidth: int, imageHeight: int):
    xOut = [x * imageWidth for x in xIn]
    yOut = [y * imageHeight for y in yIn]
    zOut = [z * imageWidth for z in zIn]
    return xOut, yOut, zOut

def PnPSolution(xIn: list, yIn: list, zIn: list, imageWidth: int, imageHeight: int):
    #https://github.com/niconielsen32/ComputerVision/blob/master/headPoseEstimation.py
    face2d = create2DFaceArray(xIn, yIn)
    #face3d = create3DFaceArray(xIn, yIn, zIn)
    face3d = createModel3DFaceArray()
    distMatrix = np.zeros((4, 1), dtype=np.float64)
    camMatrix = createCamMatrix(imageWidth, imageHeight)

    success, rotVector, translationVector = cv2.solvePnP(face3d, face2d, camMatrix, distMatrix)
    return success, rotVector, translationVector

def createEulerAngles(rotVector):
    #thanks, ChatGPT
    rotation_matrix, _ = cv2.Rodrigues(rotVector)
    sy = math.sqrt(rotation_matrix[0, 0] * rotation_matrix[0, 0] + rotation_matrix[1, 0] * rotation_matrix[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        y = math.atan2(-rotation_matrix[2, 0], sy)
        z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        y = math.atan2(-rotation_matrix[2, 0], sy)
        z = 0
    return np.array([x, y, z])

def createRotMatFromEuler(eulerAngles):
    pitch, yaw, roll = eulerAngles
    
    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(pitch), -math.sin(pitch)],
        [0, math.sin(pitch), math.cos(pitch)]
    ])
    
    Ry = np.array([
        [math.cos(yaw), 0, math.sin(yaw)],
        [0, 1, 0],
        [-math.sin(yaw), 0, math.cos(yaw)]
    ])
    
    Rz = np.array([
        [math.cos(roll), -math.sin(roll), 0],
        [math.sin(roll), math.cos(roll), 0],
        [0, 0, 1]
    ])
    
    R = Rz @ Ry @ Rx
    return R

def create_transformation_matrix(pitch, yaw, roll):
    # Create rotation matrices for each axis
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(pitch), -np.sin(pitch)],
                   [0, np.sin(pitch), np.cos(pitch)]])
    
    Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                   [0, 1, 0],
                   [-np.sin(yaw), 0, np.cos(yaw)]])
    
    Rz = np.array([[np.cos(roll), -np.sin(roll), 0],
                   [np.sin(roll), np.cos(roll), 0],
                   [0, 0, 1]])
    
    # Combine rotations
    R = np.dot(Rz, np.dot(Ry, Rx))
    return R

def transformed3DPoints(xIn: list, yIn: list, zIn: list, imageWidth: int, imageHeight: int, rotationVector, translationVector):
    euler = createEulerAngles(rotationVector)
    rotationMatrix = createRotMatFromEuler(euler)
    #xIn, yIn, zIn = scaleLandmarksToImage(xIn, yIn, zIn, imageWidth, imageHeight)
    landmarks3D = np.column_stack((xIn, yIn, zIn))
    camMatrix = createCamMatrix(imageWidth, imageHeight)
    distMatrix = np.zeros((4, 1), dtype=np.float64)

    #rotation_matrix, _ = cv2.Rodrigues(rotationVector)
    inverse_rot_matrix = np.linalg.inv(rotationMatrix)
    #transformed3DLandmarks = (inverse_rot_matrix @ landmarks3D.T).T + translationVector.T
    #transformed3DLandmarks = (inverse_rot_matrix @ (landmarks3D - translationVector.T).T).T
    transformed3DLandmarks = (inverse_rot_matrix @ (landmarks3D.T - translationVector)).T

    projected2DPoints, _ = cv2.projectPoints(transformed3DLandmarks,
                                             np.zeros((3, 1)),  # No additional rotation
                                             np.zeros((3, 1)),  # No additional translation
                                             camMatrix,
                                             distMatrix
                                            )
    
    return projected2DPoints.reshape(-1, 2)

def transformed3DPointsTest(xIn: list, yIn: list, zIn: list, rotationVector, translationVector):
    rvec_matrix, _ = cv2.Rodrigues(rotationVector)
    proj_matrix = np.hstack((rvec_matrix, translationVector))
    euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

    pitch, yaw, roll = [math.degrees(math.asin(math.sin(angle))) for angle in euler_angles]
    R = create_transformation_matrix(pitch, yaw, roll)
    RInv = np.linalg.inv(R)
    transformed3DLandmarks = []
    for x, y, z in zip(xIn, yIn, zIn):
        points = np.array([x, y, z])
        
        frontPoint = np.dot(RInv, points).tolist()
        transformed3DLandmarks.append(frontPoint)
    

    return np.array(transformed3DLandmarks)
    #return projected2DPoints.reshape(-1, 2)
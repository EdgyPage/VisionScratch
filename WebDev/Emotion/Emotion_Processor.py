#worth looking in to: ML model for facial recognition -https://www.kaggle.com/code/pabasar/facial-expression-recognition-mediapipe/notebook 
# probably 'better' than Euclidean distance if less explicable
# guidlines for smile thresholds: https://towardsdatascience.com/basic-smile-detection-using-opencv-and-dlib-aeb22afb9e67
import sys
import math
from statistics import mean 
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import Landmark_Helper as lh


def createCentroid(xIn: list, yIn: list):
    avgX = mean(xIn)
    avgY = mean(yIn)
    return (avgX, avgY)

def checkSmile(xIn: list, threshold = .36):
    #cheek points of interest
    #11, 117, 118, 123, 50, 101
    #340, 346, 347, 352, 280, 330

    lipWidth = abs(xIn[61] - xIn[291])
    jawWidth = abs(xIn[93] - xIn[323])
    ratio = lipWidth/jawWidth

    if ratio > threshold:
        return f'Smile | Lip Width / Jaw Width: {ratio}'
    else:
        return f'No Smile | Lip Width / Jaw Width: {ratio}'
    
def checkFrown(xIn: list, yIn: list):
    leftPoi = [107, 55]
    rightPoi = [336, 285]
    leftCentroid = createCentroid([xIn[x] for x in leftPoi], [yIn[y] for y in leftPoi])
    rightCentroid = createCentroid([xIn[x] for x in rightPoi], [yIn[y] for y in rightPoi])
    #168 is base of nose
    leftBrowDistToNose = round(math.sqrt((leftCentroid[0] - xIn[168])**2 + 
                           (leftCentroid[1] - yIn[168])**2), 3)
    rightBrowDistToNose = round(math.sqrt((rightCentroid[0] - xIn[168])**2 + 
                           (rightCentroid[1] - yIn[168])**2), 3)
    #133, 362 - left, right eye
    leftEyeDistToNose = round(math.sqrt((xIn[133] - xIn[168])**2 + 
                           (yIn[133] - yIn[168])**2), 3)
    rightEyeDistToNose = round(math.sqrt((xIn[362] - xIn[168])**2 + 
                           (yIn[362] - yIn[168])**2), 3)
    leftFrown = leftBrowDistToNose < leftEyeDistToNose
    rightFrown = rightBrowDistToNose < rightEyeDistToNose

    if leftFrown and rightFrown:
        return f'Frown | L-R Brow -> Nose Dist: {leftBrowDistToNose}-{rightBrowDistToNose}'
    else:
        return f'No Frown | L-R Brow -> Nose Dist: {leftBrowDistToNose}-{rightBrowDistToNose}'

def processImage(imagePath: str):
    emotionString = ''
    base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    image = mp.Image.create_from_file(imagePath)

    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(image)
    if detection_result.face_landmarks == 1:
        xs = [landmark.x for landmark in detection_result.face_landmarks[0]]
        ys = [landmark.y for landmark in detection_result.face_landmarks[0]]
        zs = [landmark.z for landmark in detection_result.face_landmarks[0]]

        xs, ys = lh.affineTransform(xs, ys)
        xs, ys, zs = lh.scalePointsFixed(xs, ys, zs)
        xs, ys = lh.alignNormalizedPointsFixed(xs, ys)

        smileResult = checkSmile(xs)
        frownResult = checkFrown(xs, ys)

        emotion = smileResult +'\n' + frownResult
        return emotion
    else:
        return 'Not exactly one face detected'

if __name__ == "__main__":
    if len(sys.argv) == 2:
        inputFramePath = r'{}'.format(sys.argv[1])
        emotion = processImage(inputFramePath)
        print(emotion)
    else:
        print(f"ERROR: Not enough or too many input arguments: {len(sys.argv)}")
        for i, arg in enumerate(sys.argv):
            print(f'Arg index: {i}')
            print(f'{arg}')
            print()
        exit()
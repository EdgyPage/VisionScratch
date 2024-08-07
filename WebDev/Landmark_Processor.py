import sys
import Landmark_Helper as lh
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp
import datetime

if len(sys.argv) == 4:
    inputVideoFilePath = r'{}'.format(sys.argv[1])
    processedVideoDir = r'{}'.format(sys.argv[2])
    videoName = r'{}'.format(sys.argv[3])
    for i, arg in enumerate(sys.argv):
        print(f'Arg index: {i}')
        print(f'Raw arg: {arg}')
        print(f'Literal arg {repr(sys.argv[i])}')
        print()
else:
    print(f"ERROR: Not enough or too many input arguments: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f'Arg index: {i}')
        print(f'{arg}')
        print()
    exit()

video = cv2.VideoCapture(inputVideoFilePath)
fps = video.get(cv2.CAP_PROP_FPS)
frameWidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
currentFrame = 0
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

plotFolderName = f'{videoName}_{timestamp}'

# Create the directory for plots
plotsDir = os.path.join(processedVideoDir, plotFolderName)

os.makedirs(plotsDir, exist_ok=True)

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face landmarker instance with the video mode:
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO)

normFrame = 'frame_'
projFrame = 'frame_proj_'

with FaceLandmarker.create_from_options(options) as landmarker:
  # The landmarker is initialized. Use it here.
  # ...
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        currentFrame += 1
        
        timestamp_ms = int(video.get(cv2.CAP_PROP_POS_MSEC) * 1000)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        results = landmarker.detect_for_video(image, timestamp_ms)
        
        if len(results.face_landmarks) == 1:
            xs = [landmark.x for landmark in results.face_landmarks[0]]
            ys = [landmark.y for landmark in results.face_landmarks[0]]
            zs = [landmark.z for landmark in results.face_landmarks[0]]

            
            xs , ys, zs, fig = lh.processFrame(xs, ys, zs, currentFrame, timestamp_ms)
            fig.savefig(f'{plotsDir}/{normFrame}{currentFrame}.png')
            plt.close(fig)
            plt.clf()

            xs = [landmark.x for landmark in results.face_landmarks[0]]
            ys = [landmark.y for landmark in results.face_landmarks[0]]
            zs = [landmark.z for landmark in results.face_landmarks[0]]
            success, rotVector, translationVector = lh.PnPSolution(xs, ys, zs, frameWidth, frameHeight)
            proj = lh.transformed3DPointsTest(xs, ys, zs, rotVector, translationVector)

            projXs = proj[:,0].tolist()
            projYs = proj[:,1].tolist()

            xs , ys, zs, fig = lh.processFrame(projXs, projYs, zs, currentFrame, timestamp_ms)
            fig.savefig(f'{plotsDir}/{projFrame}{currentFrame}.png')
            plt.close(fig)
            plt.clf()
        del image



# Input video path and graph images directory
graphs_dir = plotsDir


# Open the input video file
video = cv2.VideoCapture(inputVideoFilePath)
fps = video.get(cv2.CAP_PROP_FPS)
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

#640x480
# Prepare output video writer with new dimensions
graph_height = frame_height  # Assuming graphs have the same height as video frames
new_frame_width = frame_width * 2  # Double width for video frame + graph image



#non-proj
processedNormVideoPath = rf'{plotsDir}/{videoName}_Norm_{timestamp}.mp4'
outNorm = cv2.VideoWriter(processedNormVideoPath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (new_frame_width, frame_height))

# Iterate through frames
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
for i in range(frame_count):
    ret, frame = video.read()
    if not ret:
        break
    
    # Assuming graph images are named in sequential order (e.g., 00001.png, 00002.png, ...)
    graph_path = os.path.join(graphs_dir, f'{normFrame}{i + 1}.png')  # Adjust filename format as needed
    
    if os.path.exists(graph_path):
        graph = cv2.imread(graph_path)
        # Resize graph image to match video frame height
        graph_resized = cv2.resize(graph, (frame_width, frame_height))
        
        # Concatenate frame and graph image horizontally
        combined_frame = np.concatenate((frame, graph_resized), axis=1)
        
        # Write the combined frame to the output video
        outNorm.write(combined_frame)
    
    else:
        print(f'Graph image {graph_path} does not exist.')

# Release resources
outNorm.release()
video.release()


#proj
# Open the input video file
video = cv2.VideoCapture(inputVideoFilePath)
fps = video.get(cv2.CAP_PROP_FPS)
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

#640x480
# Prepare output video writer with new dimensions
graph_height = frame_height  # Assuming graphs have the same height as video frames
new_frame_width = frame_width * 2  # Double width for video frame + graph image

processedProjVideoPath = rf'{plotsDir}/{videoName}_Proj_{timestamp}.mp4'
outProj = cv2.VideoWriter(processedProjVideoPath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (new_frame_width, frame_height))



# Iterate through frames
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
for i in range(frame_count):
    ret, frame = video.read()
    if not ret:
        break
    
    # Assuming graph images are named in sequential order (e.g., 00001.png, 00002.png, ...)
    graph_path = os.path.join(graphs_dir, f'{projFrame}{i + 1}.png')  # Adjust filename format as needed
    
    if os.path.exists(graph_path):
        graph = cv2.imread(graph_path)
        # Resize graph image to match video frame height
        graph_resized = cv2.resize(graph, (frame_width, frame_height))
        
        # Concatenate frame and graph image horizontally
        combined_frame = np.concatenate((frame, graph_resized), axis=1)
        
        # Write the combined frame to the output video
        outProj.write(combined_frame)
    
    else:
        print(f'Graph image {graph_path} does not exist.')

# Release resources
outProj.release()
video.release()

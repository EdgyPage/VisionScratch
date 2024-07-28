import sys
import Landmark_Helper as lh
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp

if len(sys.argv) == 3:
    inputVideoFilePath = str(sys.argv[1])
    processedVideoPath = int(sys.argv[2])
else:
    print("ERROR: Not enough or too many input arguments.")
    exit()

video = cv2.VideoCapture(inputVideoFilePath)
fps = video.get(cv2.CAP_PROP_FPS)
frameWidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
currentFrame = 0

plotFolderName = f'plots_{inputVideoFilePath}'

# Get the parent directory of videoPath
parentDir = os.path.dirname(inputVideoFilePath)

# Create the directory for plots
plotsDir = os.path.join(parentDir, plotFolderName)

os.makedirs(plotsDir, exist_ok=True)

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face landmarker instance with the video mode:
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO)

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
            fig.savefig(f'{plotsDir}/frame_{currentFrame}.png')
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
            fig.savefig(f'{plotsDir}/frame_proj_{currentFrame}.png')
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
out = cv2.VideoWriter(processedVideoPath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (new_frame_width, frame_height))

# Iterate through frames
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
for i in range(frame_count):
    ret, frame = video.read()
    if not ret:
        break
    
    # Assuming graph images are named in sequential order (e.g., 00001.png, 00002.png, ...)
    graph_path = os.path.join(graphs_dir, f'frame_{i + 1}.png')  # Adjust filename format as needed
    
    if os.path.exists(graph_path):
        graph = cv2.imread(graph_path)
        # Resize graph image to match video frame height
        graph_resized = cv2.resize(graph, (frame_width, frame_height))
        
        # Concatenate frame and graph image horizontally
        combined_frame = np.concatenate((frame, graph_resized), axis=1)
        
        # Write the combined frame to the output video
        out.write(combined_frame)
    
    else:
        print(f'Graph image {graph_path} does not exist.')

# Release resources
video.release()
out.release()

import sys

if len(sys.argv) == 3:
    inputVideoFilePath = str(sys.argv[1])
    processedVideoPath = int(sys.argv[2])
else:
    print("ERROR: Not enough or too many input arguments.")
    exit()


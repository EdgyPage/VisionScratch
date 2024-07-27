<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Check if file was uploaded without errors
    if (isset($_FILES['input_video']) && $_FILES['input_video']['error'] == 0) {
        $uploadedFile = $_FILES['input_video'];
        $fileTmpPath = $uploadedFile['tmp_name'];
        $fileName = $uploadedFile['name'];
        $fileSize = $uploadedFile['size'];
        $fileType = $uploadedFile['type'];
        $fileNameCmps = explode(".", $fileName);
        $fileExtension = strtolower(end($fileNameCmps));

        // Define allowed file types
        $allowedfileExtensions = array('mp4', 'avi', 'mov');

        if (in_array($fileExtension, $allowedfileExtensions)) {
            // Directory where uploaded files will be stored
            $uploadFileDir = './uploads/';
            if (!is_dir($uploadFileDir)) {
                mkdir($uploadFileDir, 0777, true);
            }
            $dest_path = $uploadFileDir . $fileName;

            // Move the uploaded file to the server directory
            if (move_uploaded_file($fileTmpPath, $dest_path)) {
                // Process the video (e.g., using a Python script)
                $processedVideoPath = './processed/' . 'processed_' . $fileName;
                if (!is_dir('./processed/')) {
                    mkdir('./processed/', 0777, true);
                }

                // Assuming you have a Python script named Landmark_Processor.py
                // script.py inputVideoFilePath processedVideoPath
                $command = escapeshellcmd("python3 Landmark_Processor.py $dest_path $processedVideoPath");
                shell_exec($command);

                if (file_exists($processedVideoPath)) {
                    echo "Video processed successfully. <a href='$processedVideoPath'>Download processed video</a>";
                } else {
                    echo "Error: Processed video could not be found.";
                }
            } else {
                echo "Error: There was an error moving the uploaded file.";
            }
        } else {
            echo "Error: Upload failed. Allowed file types: " . implode(',', $allowedfileExtensions);
        }
    } else {
        echo "Error: " . $_FILES['input_video']['error'];
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Video Processing Result</title>
</head>
<body>
    <a href="Video_Upload.php">Upload another video</a>
</body>
</html>

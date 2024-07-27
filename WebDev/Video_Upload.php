<!DOCTYPE html>
<html>
<head>
    <title>Video Processing</title>
</head>
<body>
    <h1>Upload a Video</h1>
    <form action="Video_Processor.php" method="post" enctype="multipart/form-data">
        <input type="file" name="input_video" accept="video/*" required>
        <button type="submit">Upload and Process</button>
    </form>
</body>
</html>

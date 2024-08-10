<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $image = $data['image'];

    // Decode the base64 image
    $imageData = base64_decode(explode(',', $image)[1]);
    $tempImagePath = tempnam(sys_get_temp_dir(), 'img_') . '.jpg';
    file_put_contents($tempImagePath, $imageData);

    // Define the command to run the Python script
    $command = escapeshellcmd("python3 detect_emotion.py $tempImagePath");
    $output = shell_exec($command);

    // Clean up the temporary image file
    unlink($tempImagePath);

    // Return the emotion detected by the Python script
    echo json_encode(['emotion' => trim($output)]);
}
?>

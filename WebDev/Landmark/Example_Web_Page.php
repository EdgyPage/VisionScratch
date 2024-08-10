<!DOCTYPE html>
<html>
<head>
    <title>PHP and HTML Example</title>
</head>
<body>
    <h1>Welcome to My Web Page</h1>
    <p>This is a static paragraph in HTML.</p>

    <?php
        // PHP code block
        $message = "Hello, this is a message from PHP!";
        $currentDate = date("Y-m-d H:i:s");
    ?>

    <p><?php echo $message; ?></p>
    <p>Current Date and Time: <?php echo $currentDate; ?></p>

    <form method="post">
        <input type="text" name="user_input" placeholder="Type something">
        <button type="submit">Submit</button>
    </form>

    <?php
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            // Handle form submission
            $userInput = htmlspecialchars($_POST['user_input']);
            echo "<p>You submitted: $userInput</p>";
        }
    ?>
</body>
</html>

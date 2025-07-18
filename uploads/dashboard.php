<?php
session_start();
require_once 'includes/functions.php';

if (!is_logged_in()) {
    redirect('login.php');
}

require_once 'config/database.php';
$database = new Database();
$db = $database->getConnection();

// Get user data
$query = "SELECT * FROM users WHERE id = ?";
$stmt = $db->prepare($query);
$stmt->execute([$_SESSION['user_id']]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
?>

<?php include 'includes/header.php'; ?>

<h2>Welcome, <?php echo $user['first_name']; ?></h2>

<div class="dashboard-section">
    <h3>Your Information</h3>
    <p><strong>Name:</strong> <?php echo $user['first_name'] . ' ' . $user['last_name']; ?></p>
    <p><strong>Email:</strong> <?php echo $user['email']; ?></p>
    <p><strong>Phone:</strong> <?php echo $user['phone'] ?? 'Not provided'; ?></p>
    <p><strong>Country:</strong> <?php echo $user['country'] ?? 'Not provided'; ?></p>
    <p><strong>Passport:</strong> <?php echo $user['has_passport'] ? 'Yes' : 'No'; ?></p>
    
    <?php if (!$user['has_passport']): ?>
        <div class="alert alert-warning">
            You indicated you don't have a passport. <a href="passport.php">Click here to apply for one</a>.
        </div>
    <?php endif; ?>
</div>

<div class="dashboard-section">
    <h3>Application Status</h3>
    <p>You haven't started an application yet.</p>
    <a href="application.php" class="btn btn-primary">Start New Application</a>
</div>

<?php include 'includes/footer.php'; ?>
<?php
session_start();
require_once 'includes/functions.php';
require_once 'config/database.php';

if (!is_logged_in()) {
    redirect('login.php');
}

$database = new Database();
$db = $database->getConnection();

$errors = [];
$success = false;

// Check if user has passport
$query = "SELECT has_passport FROM users WHERE id = ?";
$stmt = $db->prepare($query);
$stmt->execute([$_SESSION['user_id']]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$user['has_passport']) {
    $_SESSION['error_message'] = "You need a valid passport to apply. Please update your profile or apply for one.";
    redirect('passport.php');
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $occupation = clean_input($_POST['occupation']);
    $experience = clean_input($_POST['experience']);
    $education_level = clean_input($_POST['education_level']);
    $language = clean_input($_POST['language']);
    $language_proficiency = clean_input($_POST['language_proficiency']);
    
    // Validate inputs
    if (empty($occupation)) $errors[] = "Occupation is required";
    if (!is_numeric($experience)) $errors[] = "Experience must be a number";
    if (empty($education_level)) $errors[] = "Education level is required";
    
    if (empty($errors)) {
        // Generate application number
        $application_number = 'WA-' . date('Ymd') . '-' . strtoupper(substr(md5(uniqid()), 0, 6));
        
        $query = "INSERT INTO applications 
                  (user_id, application_number, occupation_applied, experience_years, education, language, language_proficiency, status) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, 'submitted')";
        $stmt = $db->prepare($query);
        
        if ($stmt->execute([$_SESSION['user_id'], $application_number, $occupation, $experience, $education_level, $language, $language_proficiency])) {
            $success = true;
            
            // Send approval email
            require_once 'config/mail.php';
            $mailer = new Mailer();
            $mailer->sendApplicationApprovalEmail(
                $_SESSION['user_email'],
                $_SESSION['user_name'],
                $application_number
            );
        } else {
            $errors[] = "Application submission failed. Please try again.";
        }
    }
}
?>

<?php include 'includes/header.php'; ?>

<h2>Work Abroad Application</h2>

<?php if ($success): ?>
    <div class="alert alert-success">
        <h3>Application Submitted Successfully!</h3>
        <p>Your application has been received. We've sent you an email with further instructions.</p>
        <p><a href="dashboard.php" class="btn btn-success">Go to Dashboard</a></p>
    </div>
<?php else: ?>
    <?php if (!empty($errors)): ?>
        <div class="alert alert-danger">
            <ul>
                <?php foreach ($errors as $error): ?>
                    <li><?php echo $error; ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
    <?php endif; ?>

    <form action="application.php" method="post">
        <div class="form-section">
            <h3>Professional Information</h3>
            
            <div class="form-group">
                <label>Occupation/Profession</label>
                <input type="text" name="occupation" required>
            </div>
            
            <div class="form-group">
                <label>Years of Experience</label>
                <input type="number" name="experience" min="0" max="50" required>
            </div>
            
            <div class="form-group">
                <label>Highest Education Level</label>
                <select name="education_level" required>
                    <option value="">Select...</option>
                    <option value="high_school">High School</option>
                    <option value="diploma">Diploma</option>
                    <option value="bachelors">Bachelor's Degree</option>
                    <option value="masters">Master's Degree</option>
                    <option value="phd">PhD</option>
                </select>
            </div>
        </div>
        
        <div class="form-section">
            <h3>Language Proficiency</h3>
            
            <div class="form-group">
                <label>Language</label>
                <select name="language" required>
                    <option value="">Select...</option>
                    <option value="english">English</option>
                    <option value="french">French</option>
                    <option value="german">German</option>
                    <option value="spanish">Spanish</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Proficiency Level</label>
                <select name="language_proficiency" required>
                    <option value="">Select...</option>
                    <option value="basic">Basic</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="fluent">Fluent</option>
                    <option value="native">Native</option>
                </select>
            </div>
        </div>
        
        <button type="submit" class="btn btn-primary">Submit Application</button>
    </form>
<?php endif; ?>

<?php include 'includes/footer.php'; ?>
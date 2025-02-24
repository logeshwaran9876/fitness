# Fitness Tracker Web Application

## Overview
The **Fitness Tracker** is a web application designed to help users track their fitness activities, set goals, create workout plans, and monitor their progress. It is built using **PHP** for the backend, **MySQL** for the database, and **Bootstrap** for the frontend.

## Features
### User Authentication:
- Register a new account.
- Log in to an existing account.

### Activity Tracking:
- Log activities such as running, cycling, or walking.
- Track duration, distance, calories burned, pace, and heart rate.

### Workout Plans:
- Create custom workout plans with exercises and duration.

### Goal Setting:
- Set fitness goals (e.g., target weight, distance to run).

### View Activities:
- View all logged activities with details.


## Technologies Used

### Backend:
- Python
- MySQL (for database management)



#### Set Up the Database:

2. Create a new database named `fitness_tracker`.
3. Import the SQL file (`fitness_tracker.sql`) to create the required tables.

#### Configure Database Connection:
Edit `includes/db.php` and update the database credentials:
```php
$host = 'localhost';
$dbname = 'fitness_tracker';
$username = 'root';
$password = '';
```





## Usage
### Register:
1. Click on **Register** on the homepage.
2. Fill in the required details (username, password, age, weight, height, fitness goals).
3. Submit the form to create an account.

### Login:
1. Enter your username and password on the homepage.
2. Click **Login** to access your dashboard.

### Dashboard:
After logging in, you will be redirected to the dashboard. From here, you can:
- Track activities.
- Create workout plans.
- Set fitness goals.
- View logged activities.

### Track Activity:
1. Fill in the activity details (type, duration, distance, calories, heart rate).
2. Submit the form to log the activity.

### Create Workout Plan:
1. Enter the workout name, exercises, and duration.
2. Submit the form to save the workout plan.

### Set Goal:
1. Enter the goal type (e.g., target weight) and target value.
2. Submit the form to set the goal.

### View Activities:
- View all your logged activities with details.

### Logout:
- Click **Logout** to securely log out of your account.

## Contributing
Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a **Pull Request**.

## License
This project is licensed under the **MIT License**. See the LICENSE file for details.

## Contact
For any questions or feedback, please contact:
- **Your Name**
- **Email:** your-email@example.com
- **GitHub:** [your-username](https://github.com/your-username)


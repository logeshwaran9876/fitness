import sqlite3
import hashlib
import time
import warnings
from getpass import getpass

warnings.filterwarnings("ignore", category=Warning)

def hash_password(password):
 
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_database():
   
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            fitness_goals TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            duration REAL,
            distance REAL,
            calories REAL,
            pace REAL,
            heart_rate TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_type TEXT,
            target_value TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout_name TEXT,
            exercises TEXT,
            duration INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            challenge_description TEXT,
            status TEXT CHECK(status IN ('pending', 'completed')),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

class FitnessTracker:
    def __init__(self):
        self.conn = sqlite3.connect("fitness_tracker.db")
        self.cursor = self.conn.cursor()
        self.current_user_id = None

    def register(self, username, password, age, weight, height, fitness_goals):
       
        try:
            hashed_password = hash_password(password)
            self.cursor.execute('''
                INSERT INTO users (username, password, age, weight, height, fitness_goals)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, age, weight, height, fitness_goals))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("Error: Username already exists.")
            return False
        except Exception as e:
            print(f"Error during registration: {e}")
            return False

    def login(self, username, password):
    
        try:
            hashed_password = hash_password(password)
            self.cursor.execute('''
                SELECT id FROM users WHERE username = ? AND password = ?
            ''', (username, hashed_password))
            result = self.cursor.fetchone()

            if result:
                self.current_user_id = result[0]
                return True
            else:
                print("Error: Invalid username or password.")
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False


    def track_activity(self, activity_type, duration, distance, calories, heart_rate):
        try:
            pace = distance / (duration / 60)  # km/h
            self.cursor.execute('''
                INSERT INTO activities (user_id, activity_type, duration, distance, calories, pace, heart_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_user_id, activity_type, duration, distance, calories, pace, heart_rate))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def create_workout_plan(self, workout_name, exercises, duration):
        try:
            self.cursor.execute('''
                INSERT INTO workouts (user_id, workout_name, exercises, duration)
                VALUES (?, ?, ?, ?)
            ''', (self.current_user_id, workout_name, exercises, duration))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def set_goal(self, goal_type, target_value):
        try:
            self.cursor.execute('''
                INSERT INTO goals (user_id, goal_type, target_value)
                VALUES (?, ?, ?)
            ''', (self.current_user_id, goal_type, target_value))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def view_activities(self):
        try:
            self.cursor.execute('''
                SELECT activity_type, duration, distance, calories, pace, heart_rate FROM activities
                WHERE user_id = ?
            ''', (self.current_user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []

    def view_workouts(self):
        try:
            self.cursor.execute('''
                SELECT workout_name, exercises, duration FROM workouts
                WHERE user_id = ?
            ''', (self.current_user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []

    def view_goals(self):
        try:
            self.cursor.execute('''
                SELECT goal_type, target_value FROM goals
                WHERE user_id = ?
            ''', (self.current_user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_predefined_workout_plan(self, level):
        predefined_plans = {
            "beginner": "Walking, Bodyweight Squats, Push-ups, Yoga",
            "intermediate": "Running, Dumbbell Exercises, Planks, Jump Rope",
            "advanced": "HIIT, Weightlifting, Sprinting, Deadlifts"
        }
        return predefined_plans.get(level.lower(), "Invalid fitness level.")

    def send_friend_request(self, friend_username):
        try:
            self.cursor.execute('''
                SELECT id FROM users WHERE username = ?
            ''', (friend_username,))
            friend = self.cursor.fetchone()

            if friend:
                friend_id = friend[0]
                self.cursor.execute('''
                    INSERT INTO friends (sender_id, receiver_id, status)
                    VALUES (?, ?, 'pending')
                ''', (self.current_user_id, friend_id))
                self.conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def manage_friend_requests(self):
        try:
            self.cursor.execute('''
                SELECT f.id, u.username FROM friends f
                JOIN users u ON f.sender_id = u.id
                WHERE f.receiver_id = ? AND f.status = 'pending'
            ''', (self.current_user_id,))
            requests = self.cursor.fetchall()

            if requests:
                print("\nPending Friend Requests:")
                for req in requests:
                    print(f"{req[0]}) {req[1]}")

                request_id = input("Enter request ID to accept (or press Enter to skip): ")
                if request_id:
                    self.cursor.execute('''
                        UPDATE friends SET status = 'accepted' WHERE id = ?
                    ''', (request_id,))
                    self.conn.commit()
                    return True
            else:
                print("No pending friend requests.")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def share_challenge(self, friend_id, challenge_description):
        try:
            self.cursor.execute('''
                INSERT INTO challenges (sender_id, receiver_id, challenge_description, status)
                VALUES (?, ?, ?, 'pending')
            ''', (self.current_user_id, friend_id, challenge_description))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def view_challenges(self):
        try:
            self.cursor.execute('''
                SELECT c.id, u.username, c.challenge_description, c.status
                FROM challenges c
                JOIN users u ON c.sender_id = u.id
                WHERE c.receiver_id = ?
            ''', (self.current_user_id,))
            challenges = self.cursor.fetchall()

            if challenges:
                print("\nChallenges Shared with You:")
                for challenge in challenges:
                    print(f"ID: {challenge[0]}, From: {challenge[1]}, Challenge: {challenge[2]}")
            else:
                print("No challenges found.")
            return challenges
        except Exception as e:
            print(f"Error: {e}")
            return []

    def logout(self):
        self.current_user_id = None

    def close(self):
        self.conn.close()


class FitnessTrackerConsole:
    def __init__(self):
        self.tracker = FitnessTracker()

    def main_menu(self):
        while True:
            print("\n--- Fitness Tracker ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.register_page()
            elif choice == "2":
                if self.login_page():
                    self.user_dashboard()
            elif choice == "3":
                self.tracker.close()
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def register_page(self):
        print("\n--- Register ---")
        username = input("Enter a username: ")
        password = getpass("Enter a password: ") 
        age = int(input("Enter your age: "))
        weight = float(input("Enter your weight (kg): "))
        height = float(input("Enter your height (cm): "))
        fitness_goals = input("Enter your fitness goals: ")

        if self.tracker.register(username, password, age, weight, height, fitness_goals):
            print("Registration successful!")
        else:
            print("Error: Username already exists or invalid input.")

    def login_page(self):
        print("\n--- Login ---")
        username = input("Enter your username: ")
        password = getpass("Enter your password: ") 

        if self.tracker.login(username, password):
            print("Login successful!")
            return True
        else:
            print("Invalid username or password.")
            return False

    def user_dashboard(self):
        while True:
            print("\n--- User Dashboard ---")
            print("1. Track Activity")
            print("2. Create Workout Plan")
            print("3. Set Goal")
            print("4. View Activities")
            print("5. View Workout Plans")
            print("6. View Goals")
            print("7. Social Features")
            print("8. Logout")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.track_activity_page()
            elif choice == "2":
                self.create_workout_page()
            elif choice == "3":
                self.set_goal_page()
            elif choice == "4":
                self.view_activities_page()
            elif choice == "5":
                self.view_workouts_page()
            elif choice == "6":
                self.view_goals_page()
            elif choice == "7":
                self.social_features_page()
            elif choice == "8":
                self.tracker.logout()
                print("Logged out successfully!")
                break
            else:
                print("Invalid choice. Please try again.")

    def track_activity_page(self):
        print("\n--- Track Activity ---")
        activity_type = input("Enter activity type (e.g., running, walking, cycling): ")

     
        print("\nStarting timer... Press Enter to stop.")
        input("Press Enter to start the timer.")
        start_time = time.time()
        input("Press Enter to stop the timer.")
        end_time = time.time()
        duration = (end_time - start_time) / 60 s
        print(f"Activity duration: {duration:.2f} minutes")

      
        weight = self.tracker.cursor.execute('SELECT weight FROM users WHERE id = ?', (self.tracker.current_user_id,)).fetchone()[0]
        if activity_type.lower() == "running":
            calories = 10 * weight * (duration / 60)  
        elif activity_type.lower() == "cycling":
            calories = 8 * weight * (duration / 60) 
        elif activity_type.lower() == "walking":
            calories = 5 * weight * (duration / 60)  
        else:
            calories = 0

        print(f"Calories burned: {calories:.2f} cal")

        distance = float(input("Enter distance covered (km): "))
        heart_rate = input("Enter heart rate (optional, press Enter to skip): ")

        if self.tracker.track_activity(activity_type, duration, distance, calories, heart_rate):
            print("Activity recorded successfully!")
        else:
            print("Failed to record activity.")

    def create_workout_page(self):
        print("\n--- Create Workout Plan ---")
        workout_name = input("Enter workout name (e.g., Full Body Strength, Cardio Burn): ")
        exercises = input("Enter exercises (comma-separated, e.g., Squats, Push-ups, Burpees): ")
        duration = int(input("Enter workout duration (minutes): "))

        if self.tracker.create_workout_plan(workout_name, exercises, duration):
            print("Workout plan created successfully!")
        else:
            print("Failed to create workout plan.")

    def set_goal_page(self):
        print("\n--- Set Goal ---")
        goal_type = input("Enter the goal type (e.g., target weight, distance to run): ")
        target_value = input("Enter the target value: ")

        if self.tracker.set_goal(goal_type, target_value):
            print("Goal set successfully!")
        else:
            print("Failed to set goal.")

    def view_activities_page(self):
        print("\n--- View Activities ---")
        activities = self.tracker.view_activities()
        if not activities:
            print("No activities recorded yet.")
        else:
            for idx, activity in enumerate(activities, 1):
                print(f"{idx}. {activity[0]} - {activity[1]} min, {activity[2]} km, {activity[3]} cal, Pace: {activity[4]:.2f} km/h")
                if activity[5]:
                    print(f"   Heart Rate: {activity[5]} bpm")

    def view_workouts_page(self):
        print("\n--- View Workout Plans ---")
        workouts = self.tracker.view_workouts()
        if not workouts:
            print("No workout plans recorded yet.")
        else:
            for idx, workout in enumerate(workouts, 1):
                print(f"{idx}. {workout[0]} - Exercises: {workout[1]}, Duration: {workout[2]} minutes")

    def view_goals_page(self):
        print("\n--- View Goals ---")
        goals = self.tracker.view_goals()
        if not goals:
            print("No goals recorded yet.")
        else:
            for idx, goal in enumerate(goals, 1):
                print(f"{idx}. {goal[0]} - Target: {goal[1]}")

    def social_features_page(self):
        while True:
            print("\n--- Social Features ---")
            print("1. Send Friend Request")
            print("2. Manage Friend Requests")
            print("3. Share Challenge with Friends")
            print("4. View Challenges")
            print("5. Back to Main Menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                friend_username = input("Enter friend's username: ")
                if self.tracker.send_friend_request(friend_username):
                    print("Friend request sent!")
                else:
                    print("Failed to send friend request.")
            elif choice == "2":
                if self.tracker.manage_friend_requests():
                    print("Friend request accepted!")
                else:
                    print("No pending friend requests.")
            elif choice == "3":
                friend_id = input("Enter friend's ID: ")
                challenge_description = input("Enter challenge description: ")
                if self.tracker.share_challenge(friend_id, challenge_description):
                    print("Challenge shared!")
                else:
                    print("Failed to share challenge.")
            elif choice == "4":
                self.tracker.view_challenges()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    initialize_database()
    app = FitnessTrackerConsole()
    app.main_menu()    

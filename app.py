import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import hashlib
import os


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()

    # Drop existing tables (for debugging)
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS activities")
    cursor.execute("DROP TABLE IF EXISTS goals")
    cursor.execute("DROP TABLE IF EXISTS workouts")

    # Create Users Table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            fitness_goals TEXT
        )
    ''')

    # Create Activities Table
    cursor.execute('''
        CREATE TABLE activities (
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

    # Create Goals Table
    cursor.execute('''
        CREATE TABLE goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_type TEXT,
            target_value TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create Workouts Table
    cursor.execute('''
        CREATE TABLE workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout_name TEXT,
            exercises TEXT,
            duration INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Fitness Tracker Class (Same as before)
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
            return False
        except Exception as e:
            print(f"Error: {e}")
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
                return False
        except Exception as e:
            print(f"Error: {e}")
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

    def logout(self):
        self.current_user_id = None

    def close(self):
        self.conn.close()

# CustomTkinter UI
class FitnessTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.root.geometry("800x600")  # Set window size
        self.tracker = FitnessTracker()

        self.main_menu()

    def main_menu(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Welcome to Fitness Tracker", font=("Arial", 24)).pack(pady=20)

        ctk.CTkButton(self.root, text="Register", command=self.register_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Login", command=self.login_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Exit", command=self.root.quit, width=200, height=40).pack(pady=10)

    def register_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Register", font=("Arial", 20)).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self.root, placeholder_text="Username", width=300)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=10)

        self.age_entry = ctk.CTkEntry(self.root, placeholder_text="Age", width=300)
        self.age_entry.pack(pady=10)

        self.weight_entry = ctk.CTkEntry(self.root, placeholder_text="Weight (kg)", width=300)
        self.weight_entry.pack(pady=10)

        self.height_entry = ctk.CTkEntry(self.root, placeholder_text="Height (cm)", width=300)
        self.height_entry.pack(pady=10)

        self.goals_entry = ctk.CTkEntry(self.root, placeholder_text="Fitness Goals", width=300)
        self.goals_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Register", command=self.register_user, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Back", command=self.main_menu, width=200, height=40).pack(pady=5)

    def login_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Login", font=("Arial", 20)).pack(pady=20)

        self.login_username_entry = ctk.CTkEntry(self.root, placeholder_text="Username", width=300)
        self.login_username_entry.pack(pady=10)

        self.login_password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*", width=300)
        self.login_password_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Login", command=self.login_user, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Back", command=self.main_menu, width=200, height=40).pack(pady=5)

    def user_dashboard(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="User Dashboard", font=("Arial", 20)).pack(pady=20)

        ctk.CTkButton(self.root, text="Track Activity", command=self.track_activity_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Create Workout Plan", command=self.create_workout_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Set Goal", command=self.set_goal_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="View Activities", command=self.view_activities_page, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Logout", command=self.logout_user, width=200, height=40).pack(pady=10)

    def track_activity_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Track Activity", font=("Arial", 20)).pack(pady=20)

        self.activity_type_entry = ctk.CTkEntry(self.root, placeholder_text="Activity Type", width=300)
        self.activity_type_entry.pack(pady=10)

        self.duration_entry = ctk.CTkEntry(self.root, placeholder_text="Duration (minutes)", width=300)
        self.duration_entry.pack(pady=10)

        self.distance_entry = ctk.CTkEntry(self.root, placeholder_text="Distance (km)", width=300)
        self.distance_entry.pack(pady=10)

        self.calories_entry = ctk.CTkEntry(self.root, placeholder_text="Calories Burned", width=300)
        self.calories_entry.pack(pady=10)

        self.heart_rate_entry = ctk.CTkEntry(self.root, placeholder_text="Heart Rate (optional)", width=300)
        self.heart_rate_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Submit", command=self.submit_activity, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Back", command=self.user_dashboard, width=200, height=40).pack(pady=5)

    def create_workout_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Create Workout Plan", font=("Arial", 20)).pack(pady=20)

        self.workout_name_entry = ctk.CTkEntry(self.root, placeholder_text="Workout Name", width=300)
        self.workout_name_entry.pack(pady=10)

        self.exercises_entry = ctk.CTkEntry(self.root, placeholder_text="Exercises (comma-separated)", width=300)
        self.exercises_entry.pack(pady=10)

        self.workout_duration_entry = ctk.CTkEntry(self.root, placeholder_text="Duration (minutes)", width=300)
        self.workout_duration_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Submit", command=self.submit_workout, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Back", command=self.user_dashboard, width=200, height=40).pack(pady=5)

    def set_goal_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="Set Goal", font=("Arial", 20)).pack(pady=20)

        self.goal_type_entry = ctk.CTkEntry(self.root, placeholder_text="Goal Type", width=300)
        self.goal_type_entry.pack(pady=10)

        self.target_value_entry = ctk.CTkEntry(self.root, placeholder_text="Target Value", width=300)
        self.target_value_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Submit", command=self.submit_goal, width=200, height=40).pack(pady=10)
        ctk.CTkButton(self.root, text="Back", command=self.user_dashboard, width=200, height=40).pack(pady=5)

    def view_activities_page(self):
        self.clear_frame()
        ctk.CTkLabel(self.root, text="View Activities", font=("Arial", 20)).pack(pady=20)

        activities = self.tracker.view_activities()
        if not activities:
            ctk.CTkLabel(self.root, text="No activities recorded yet.").pack()
        else:
            for activity in activities:
                ctk.CTkLabel(self.root, text=f"{activity[0]} - {activity[1]} min, {activity[2]} km, {activity[3]} cal, Pace: {activity[4]:.2f} km/h").pack()

        ctk.CTkButton(self.root, text="Back", command=self.user_dashboard, width=200, height=40).pack(pady=10)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        age = int(self.age_entry.get())
        weight = float(self.weight_entry.get())
        height = float(self.height_entry.get())
        fitness_goals = self.goals_entry.get()

        if self.tracker.register(username, password, age, weight, height, fitness_goals):
            messagebox.showinfo("Success", "Registration successful!")
            self.main_menu()
        else:
            messagebox.showerror("Error", "Username already exists or invalid input.")

    def login_user(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if self.tracker.login(username, password):
            messagebox.showinfo("Success", "Login successful!")
            self.user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def submit_activity(self):
        activity_type = self.activity_type_entry.get()
        duration = float(self.duration_entry.get())
        distance = float(self.distance_entry.get())
        calories = float(self.calories_entry.get())
        heart_rate = self.heart_rate_entry.get()

        if self.tracker.track_activity(activity_type, duration, distance, calories, heart_rate):
            messagebox.showinfo("Success", "Activity recorded successfully!")
            self.user_dashboard()
        else:
            messagebox.showerror("Error", "Failed to record activity.")

    def submit_workout(self):
        workout_name = self.workout_name_entry.get()
        exercises = self.exercises_entry.get()
        duration = int(self.workout_duration_entry.get())

        if self.tracker.create_workout_plan(workout_name, exercises, duration):
            messagebox.showinfo("Success", "Workout plan created successfully!")
            self.user_dashboard()
        else:
            messagebox.showerror("Error", "Failed to create workout plan.")

    def submit_goal(self):
        goal_type = self.goal_type_entry.get()
        target_value = self.target_value_entry.get()

        if self.tracker.set_goal(goal_type, target_value):
            messagebox.showinfo("Success", "Goal set successfully!")
            self.user_dashboard()
        else:
            messagebox.showerror("Error", "Failed to set goal.")

    def logout_user(self):
        self.tracker.logout()
        messagebox.showinfo("Success", "Logged out successfully!")
        self.main_menu()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run the Application
if __name__ == "__main__":
    initialize_database()
    root = ctk.CTk()
    app = FitnessTrackerApp(root)
    root.mainloop()

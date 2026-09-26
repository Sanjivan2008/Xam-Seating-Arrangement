import random
import csv
import os
import mysql.connector

# Set your MySQL password in the MYSQL_PASSWORD environment variable.
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
if not MYSQL_PASSWORD:
    raise RuntimeError("MYSQL_PASSWORD environment variable is not set.")
from typing import List, Tuple


# ------------------------------------------------------------
# AUTO-CREATE DATABASE
# ------------------------------------------------------------
def initialize_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=MYSQL_PASSWORD
    )
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS exam_seating_system")
    db.commit()
    cursor.close()
    db.close()


# ------------------------------------------------------------
# CONNECT TO PROGRAM DATABASE
# ------------------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=MYSQL_PASSWORD,
        database="exam_seating_system"
    )


# ------------------------------------------------------------
# CLASS DEFINITIONS
# ------------------------------------------------------------
class Student:
    def __init__(self, roll_no: str, name: str, class_name: str, gender: str):
        self.roll_no = roll_no
        self.name = name
        self.class_name = class_name
        self.gender = gender
    
    def __repr__(self):
        return f"{self.roll_no}({self.class_name}-{self.gender})"


class ExamHall:
    def __init__(self, hall_number: int, rows: int, columns: int, students_per_desk: int):
        self.hall_number = hall_number
        self.rows = rows
        self.columns = columns
        self.students_per_desk = students_per_desk
        self.total_desks = rows * columns
        self.total_capacity = self.total_desks * students_per_desk
        
        self.seating_arrangement = [[[None for _ in range(students_per_desk)] 
                                     for _ in range(columns)] 
                                    for _ in range(rows)]
    
    def is_valid_placement(self, student: Student, row: int, col: int, seat: int) -> bool:
        
        for s in range(self.students_per_desk):
            if self.seating_arrangement[row][col][s] is not None:
                existing = self.seating_arrangement[row][col][s]
                
                if existing.class_name == student.class_name:
                    return False
                
                if existing.gender == student.gender:
                    return False
        
        adjacent_positions = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1)
        ]
        
        for adj_row, adj_col in adjacent_positions:
            if 0 <= adj_row < self.rows and 0 <= adj_col < self.columns:
                for s in range(self.students_per_desk):
                    if self.seating_arrangement[adj_row][adj_col][s] is not None:
                        existing = self.seating_arrangement[adj_row][adj_col][s]
                        if existing.class_name == student.class_name:
                            return False
        
        return True
    
    def arrange_students(self, students: List[Student]) -> Tuple[bool, List[Student]]:
        if len(students) > self.total_capacity:
            print(f"Error: {len(students)} students cannot fit in {self.total_capacity} seats!")
            return False, []
        
        students_copy = students.copy()
        random.shuffle(students_copy)
        
        placed_students = []
        failed_students = []
        
        for student in students_copy:
            placed = False
            attempts = 0
            max_attempts = self.total_capacity * 3
            
            while not placed and attempts < max_attempts:
                row = random.randint(0, self.rows - 1)
                col = random.randint(0, self.columns - 1)
                seat = random.randint(0, self.students_per_desk - 1)
                
                if (self.seating_arrangement[row][col][seat] is None and 
                    self.is_valid_placement(student, row, col, seat)):
                    self.seating_arrangement[row][col][seat] = student
                    placed = True
                    placed_students.append(student)
                
                attempts += 1
            
            if not placed:
                failed_students.append(student)
        
        if failed_students:
            return False, failed_students
        
        return True, []
    
    def seat_students_randomly(self, students: List[Student]) -> bool:
        
        placed_count = 0
        
        for student in students:
            placed = False
            
            for row in range(self.rows):
                for col in range(self.columns):
                    for seat in range(self.students_per_desk):
                        if self.seating_arrangement[row][col][seat] is None:
                            self.seating_arrangement[row][col][seat] = student
                            placed = True
                            placed_count += 1
                            break
                    if placed:
                        break
                if placed:
                    break
            
            if not placed:
                print(f"No empty seats available for {student.name}")
                return False
        
        print(f"\n✓ Successfully seated {placed_count} additional students randomly")
        return True
    
    def display_arrangement(self):
        
        print(f"\n{'='*100}")
        print(f"HALL {self.hall_number} | Rows: {self.rows} | Cols: {self.columns} | Students/Desk: {self.students_per_desk}")
        print('='*100)
        
        for row in range(self.rows):
            print(f"\nROW {row + 1}:")
            for col in range(self.columns):
                desk_num = row * self.columns + col + 1
                students_at_desk = []
                for seat in range(self.students_per_desk):
                    student = self.seating_arrangement[row][col][seat]
                    if student:
                        students_at_desk.append(f"{student.name}({student.roll_no}-{student.class_name}-{student.gender})")
                    else:
                        students_at_desk.append("[EMPTY]")
                print(f"  D{desk_num}: {' | '.join(students_at_desk)}")


def load_students_from_csv(filename: str, roll_col: str, name_col: str, class_col: str, gender_col: str) -> List[Student]:
    
    students = []
    
    if not os.path.exists(filename):
        print(f"\n✗ Error: File '{filename}' not found!")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            if csv_reader.fieldnames is None:
                print("✗ Error: CSV file invalid!")
                return None
            
            available_columns = [col.strip() for col in csv_reader.fieldnames]
            provided_columns = [roll_col, name_col, class_col, gender_col]
            
            for col in provided_columns:
                if col not in available_columns:
                    print(f"✗ Missing column: {col}")
                    return None
            
            for i, row in enumerate(csv_reader, start=2):
                
                try:
                    roll_no = row.get(roll_col, '').strip()
                    name = row.get(name_col, '').strip()
                    class_name = row.get(class_col, '').strip()
                    gender = row.get(gender_col, '').strip().upper()
                    
                    if not roll_no or not name or not class_name or not gender:
                        print(f"⚠ Row {i} has missing data. Skipping.")
                        continue
                    
                    if gender in ['MALE', 'BOY', 'BOYS']:
                        gender = 'M'
                    elif gender in ['FEMALE', 'GIRL', 'GIRLS']:
                        gender = 'F'
                    
                    if gender not in ['M', 'F']:
                        print(f"⚠ Invalid gender in row {i}. Skipping.")
                        continue
                    
                    students.append(Student(roll_no, name, class_name, gender))
                
                except Exception as e:
                    print(f"⚠ Row {i} error: {e}")
                    continue
        
        print(f"\n✓ Loaded {len(students)} students")
        return students
    
    except Exception as e:
        print(f"\n✗ Error reading CSV: {e}")
        return None


# ------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------
def main():

    # AUTO CREATE DATABASE AT START
    initialize_database()
    
    print("\nSTEP 0: ADMIN LOGIN")
    print("-"*100)
    admin_name = input("Enter admin name: ").strip()

    db = get_db_connection()
    cursor = db.cursor()

    # AUTO CREATE LOG TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_name VARCHAR(100),
            action VARCHAR(200),
            time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

    cursor.execute(
        "INSERT INTO admin_log (admin_name, action) VALUES (%s, %s)",
        (admin_name, "Started seating arrangement process")
    )
    db.commit()

    print("="*100)
    print("EXAM SEATING ARRANGEMENT SYSTEM")
    print("="*100)
    
    print("\nSTEP 1: LOAD STUDENT DATA")
    print("-"*100)
    csv_path = input("Enter CSV file path: ").strip()
    
    if not os.path.exists(csv_path):
        print(f"✗ Error: File '{csv_path}' not found!")
        return
    
    print("\nEnter column names from CSV:")
    roll_col = input("  Roll Number column: ").strip()
    name_col = input("  Name column: ").strip()
    class_col = input("  Class column: ").strip()
    gender_col = input("  Gender column: ").strip()
    
    students = load_students_from_csv(csv_path, roll_col, name_col, class_col, gender_col)
    
    if students is None:
        return
    
    classes = {}
    genders = {"M": 0, "F": 0}
    
    for student in students:
        classes[student.class_name] = classes.get(student.class_name, 0) + 1
        genders[student.gender] += 1
    
    print(f"\nTotal: {len(students)} | Boys: {genders['M']} | Girls: {genders['F']}")
    
    print("\nSTEP 2: CONFIGURE EXAM HALLS")
    print("-"*100)
    
    try:
        num_halls = int(input("Number of exam halls: "))
        
        exam_halls = []
        total_capacity = 0
        
        for i in range(num_halls):
            print(f"Hall {i+1}:")
            rows = int(input("  Rows: "))
            columns = int(input("  Columns: "))
            students_per_desk = int(input("  Students per desk: "))
            
            hall = ExamHall(i+1, rows, columns, students_per_desk)
            exam_halls.append(hall)
            total_capacity += hall.total_capacity
        
        print(f"\nTotal capacity: {total_capacity}")
        
        if len(students) > total_capacity:
            print("✗ Error: Not enough seats")
            return
    
    except ValueError:
        print("✗ Invalid number!")
        return
    
    print("\nSTEP 3: ARRANGE STUDENTS")
    print("-"*100)
    print("Constraints:")
    print("  1. Same class cannot sit same/adjacent")
    print("  2. Boys/Girls cannot share desk")
    input("Press Enter to start...")
    
    remaining_students = students.copy()
    all_failed = []
    
    for hall in exam_halls:
        if not remaining_students:
            break
        
        students_for_hall = remaining_students[:hall.total_capacity]
        remaining_students = remaining_students[hall.total_capacity:]
        
        print(f"\nHall {hall.hall_number}: Seating {len(students_for_hall)} students...")
        
        success, failed = hall.arrange_students(students_for_hall)
        
        if not success and failed:
            print(f"⚠ {len(failed)} students failed to place.")
            
            choice = input("Seat them randomly? (y/n): ").lower()
            
            if choice == 'y':
                hall.seat_students_randomly(failed)
            else:
                all_failed.extend(failed)
    
    print("\n" + "="*100)
    print("FINAL SEATING ARRANGEMENT")
    print("="*100)
    
    for hall in exam_halls:
        hall.display_arrangement()
    
    if all_failed:
        print(f"\n⚠ {len(all_failed)} students unseated.")
    
    cursor.execute(
        "INSERT INTO admin_log (admin_name, action) VALUES (%s, %s)",
        (admin_name, "Completed seating arrangement")
    )
    db.commit()
    cursor.close()
    db.close()

    print("\nDONE.")


if __name__ == "__main__":
    main()

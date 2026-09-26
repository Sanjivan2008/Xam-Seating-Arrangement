# Xam Seating Arrangement

A Python and MySQL-based exam seating arrangement system designed to automate the allocation of students across examination halls while following seating constraints.

## About the Project

The Xam Seating Arrangement System was developed to simplify the process of assigning students to examination halls.

The program imports student information from a CSV file, allows the administrator to configure examination halls, and automatically generates seating arrangements based on predefined constraints.

## Features

- Import student details from a CSV file
- Automatic MySQL database creation
- Admin activity logging using MySQL
- Configure multiple examination halls
- Set rows, columns, and students per desk
- Automatically calculate hall capacity
- Randomized student allocation
- Validate student information before allocation
- Display the final seating arrangement hall-by-hall
- Handle students who cannot initially be allocated

## Seating Constraints

The system attempts to follow these rules:

1. Students from the same class cannot share the same desk.
2. Students from the same class cannot sit directly adjacent to each other.
3. Students of the same gender cannot share the same desk.
4. The system checks whether the available examination hall capacity is sufficient before allocation.

## Technologies Used

- Python
- MySQL
- CSV
- Object-Oriented Programming (OOP)
- `mysql-connector-python`

## Requirements

Before running the project, install:

- Python 3
- MySQL Server
- MySQL Connector for Python

Install the required Python package using:

```bash
pip install mysql-connector-python

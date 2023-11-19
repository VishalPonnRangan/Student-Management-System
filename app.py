from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

student_fields = ['roll', 'name', 'age', 'dob', 'class', 'subjects', 'marks', 'percentage', 'grade']
student_database = 'students.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def show_students():
    students = load_students()
    return render_template('students.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_data = {}
        for field in student_fields:
            value = request.form.get(field)
            if field in ('subjects', 'marks'):
                values_list = value.split(', ')
                if field == 'marks':
                    values_list = [int(mark) for mark in values_list]
                student_data[field] = values_list
            else:
                student_data[field] = value

        calculate_percentage_and_grade(student_data)

        save_student(student_data)
        return redirect(url_for('show_students'))

    return render_template('add_student.html')

@app.route('/search_student', methods=['GET', 'POST'])
def search_student():
    if request.method == 'POST':
        roll = request.form.get('roll')
        student = find_student(roll)
        return render_template('search_student.html', student=student)

    return render_template('search_student.html', student=None)

@app.route('/delete_student/<roll>')
def delete_student(roll):
    delete_student_by_roll(roll)
    return redirect(url_for('show_students'))

@app.route('/update_student/<roll>', methods=['GET', 'POST'])
def update_student(roll):
    if request.method == 'POST':
        updated_data = {}
        for field in student_fields:
            value = request.form.get(field)
            if field == 'age':

                try:
                    updated_data[field] = int(value.strip())
                except ValueError:

                    updated_data[field] = None
            elif field in ('subjects', 'marks'):
                values_list = value.split(', ')
                if field == 'marks':
                    values_list = [int(mark) for mark in values_list]
                updated_data[field] = values_list
            else:
                updated_data[field] = value

        calculate_percentage_and_grade(updated_data)

        update_student_by_roll(roll, updated_data)
        return redirect(url_for('show_students'))

    student = find_student(roll)
    return render_template('update_student.html', student=student)

def load_students():
    students = []
    with open(student_database, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=student_fields)
        next(reader)
        students = [row for row in reader]
    return students

def save_student(student_data):
    with open(student_database, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=student_fields)
        writer.writerow(student_data)

def update_student_by_roll(roll, updated_data):
    students = load_students()
    updated_students = [updated_data if student['roll'] == roll else student for student in students]

    with open(student_database, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=student_fields)
        writer.writeheader()
        writer.writerows(updated_students)

def calculate_percentage_and_grade(student_data):
    marks = student_data['marks']
    total_marks = sum(marks)
    percentage = (total_marks / (len(marks) * 100)) * 100

    if percentage >= 90:
        grade = 'A+'
    elif 80 <= percentage < 90:
        grade = 'A'
    elif 70 <= percentage < 80:
        grade = 'B'
    elif 60 <= percentage < 70:
        grade = 'C'
    elif 50 <= percentage < 60:
        grade = 'D'
    else:
        grade = 'F'

    student_data['percentage'] = round(percentage, 2)
    student_data['grade'] = grade

def find_student(roll):
    students = load_students()
    for student in students:
        if student['roll'] == roll:
            return student
    return None

def delete_student_by_roll(roll):
    students = load_students()
    updated_students = [student for student in students if student['roll'] != roll]

    with open(student_database, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=student_fields)
        writer.writeheader()
        writer.writerows(updated_students)

if __name__ == '__main__':
    app.run(debug=True)
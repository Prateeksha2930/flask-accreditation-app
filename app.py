from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # needed for flash messages

# DB connection helper
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    # Show some info or main page
    return render_template('index.html')

@app.route('/add_program', methods=['GET', 'POST'])
def add_program():
    years = list(range(2019, 2061))  # 2061 is exclusive
    if request.method == 'POST':
        
        program_code = request.form['program_code'].strip().upper()
        year = request.form['year'].strip()
        department_name = request.form['department_name'].strip()
        director_faculty = request.form['director_faculty'].strip()


        program_id = f"{program_code}_{year[-2:]}"  # same ID logic

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ProgramID FROM PROGRAM WHERE ProgramID = %s", (program_id,))
        exists = cursor.fetchone()

        if exists:
            flash(f"Program {program_id} already exists!", "warning")
        else:
            cursor.execute("INSERT INTO PROGRAM (ProgramID, AcademicYear, DepartmentName, DirectorFaculty) VALUES (%s, %s, %s, %s)",
                           (program_id, year, department_name, director_faculty))
            conn.commit()
            flash(f"Program {program_id} added successfully.", "success")

        cursor.close()
        conn.close()

        return redirect(url_for('add_program'))

    return render_template('add_program.html', years = years)

# after add_program...


@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Ensure results are dictionaries

    # Fetch all program details
    cursor.execute("SELECT ProgramID, DepartmentName FROM PROGRAM")
    programs = cursor.fetchall()  # List of dicts like {'ProgramID': 'CS_25', 'DepartmentName': 'CS'}

    goal_id = ""
    if request.method == 'POST':
        program_id = request.form['program_id']
        goal_desc = request.form['goal_description']

        # Generate GoalID
        base = program_id.replace("_", "")
        cursor.execute("SELECT GoalID FROM GOAL WHERE ProgramID=%s ORDER BY GoalID DESC LIMIT 1", (program_id,))
        last = cursor.fetchone()
        if last:
            last_num = int(last['GoalID'].split('G')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        goal_id = f"{base}G{next_num:02d}"

        # Insert into DB
        cursor.execute(
            "INSERT INTO GOAL (GoalID, ProgramID, GoalDescription) VALUES (%s, %s, %s)",
            (goal_id, program_id, goal_desc)
        )
        conn.commit()
        flash(f"✅ Goal {goal_id} added to {program_id}", "success")
        return redirect(url_for('add_goal'))

    cursor.close()
    conn.close()

    return render_template('add_goal.html', programs=programs)

@app.route('/get_next_goal_id')
def get_next_goal_id():
    program_id = request.args.get('program_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    base = program_id.replace("_", "")
    cursor.execute("SELECT GoalID FROM GOAL WHERE ProgramID = %s ORDER BY GoalID DESC LIMIT 1", (program_id,))
    last = cursor.fetchone()
    if last:
        last_num = int(last[0].split('G')[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    new_goal_id = f"{base}G{next_num:02d}"

    cursor.close()
    conn.close()

    return {'goal_id': new_goal_id}


@app.route('/add_objective', methods=['GET', 'POST'])
def add_objective():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT GoalID, GoalDescription FROM GOAL")
    goals = cursor.fetchall()

    if request.method == 'POST':
        goal_id = request.form['goal_id']
        desc = request.form['objective_desc']

        # Generate ObjectiveID
        cursor.execute(
            "SELECT ObjectiveID FROM OBJECTIVE WHERE GoalID=%s ORDER BY ObjectiveID DESC LIMIT 1",
            (goal_id,)
        )
        last = cursor.fetchone()
        if last:
            last_num = int(last[0].split('O')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        objective_id = f"{goal_id}O{next_num:02d}"

        cursor.execute(
            "INSERT INTO OBJECTIVE (ObjectiveID, GoalID, ObjDescription) VALUES (%s, %s, %s)",
            (objective_id, goal_id, desc)
        )
        conn.commit()
        flash(f"Objective {objective_id} added.", "success")
        return redirect(url_for('add_objective'))

    cursor.close()
    conn.close()
    return render_template('add_objective.html', goals=goals)

from flask import jsonify

@app.route('/next_objective_id/<goal_id>')
def next_objective_id(goal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ObjectiveID FROM OBJECTIVE WHERE GoalID=%s ORDER BY ObjectiveID DESC LIMIT 1", (goal_id,))
    last = cursor.fetchone()
    if last:
        last_num = int(last[0].split('O')[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    next_id = f"{goal_id}O{next_num:02d}"
    cursor.close()
    conn.close()
    return jsonify({'next_objective_id': next_id})



@app.route('/add_rubric', methods=['GET', 'POST'])
def add_rubric():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all objectives for dropdown
    cursor.execute("SELECT ObjectiveID, ObjDescription FROM OBJECTIVE")
    objectives = cursor.fetchall()

    if request.method == "POST":
        objective_id = request.form['objective_id']
        criteria = request.form['rubric_criteria']

        # Generate RubricID
        rubric_id = generate_rubric_id(objective_id, cursor)

        # Insert into database
        cursor.execute("INSERT INTO RUBRIC (RubricID, ObjectiveID, Criteria) VALUES (%s, %s, %s)",
                       (rubric_id, objective_id, criteria))
        conn.commit()
        flash(f"Rubric {rubric_id} added successfully.", "success")

        cursor.close()
        conn.close()
        return redirect(url_for('add_rubric'))

    cursor.close()
    conn.close()
    return render_template('add_rubric.html', objectives=objectives)

def generate_rubric_id(objective_id, cursor):
    base = objective_id.split('O')[0]
    obj_num = int(objective_id.split('O')[1])
    offset = (obj_num - 1) * 10

    cursor.execute("SELECT RubricID FROM RUBRIC WHERE ObjectiveID=%s ORDER BY RubricID DESC LIMIT 1", (objective_id,))
    last = cursor.fetchone()
    last_num = int(last[0].split('R')[-1]) if last else 0
    next_num = last_num + 1 or 1 + offset
    return f"{base}R{next_num:02d}"

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch existing CourseIDs
    cursor.execute("SELECT CourseID FROM COURSE")
    existing_courses = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        selected_course = request.form.get('existing_course')
        new_course_id = request.form.get('new_course_id')
        course_description = request.form.get('course_description')

        course_id_to_use = new_course_id.strip() if new_course_id else selected_course

        if not course_id_to_use or not course_description:
            flash("Course ID and description are required.", "danger")
        else:
            # Check if course already exists
            cursor.execute("SELECT * FROM COURSE WHERE CourseID = %s", (course_id_to_use,))
            existing = cursor.fetchone()
            if existing:
                flash(f"Course ID '{course_id_to_use}' already exists.", "warning")
            else:
                cursor.execute("INSERT INTO COURSE (CourseID, CourseName) VALUES (%s, %s)",
                               (course_id_to_use, course_description))
                conn.commit()
                flash(f"Course '{course_id_to_use}' added successfully!", "success")
            return redirect(url_for('add_course'))

    cursor.close(); conn.close()
    return render_template('add_course.html', courses=existing_courses)


@app.route('/add_curriculum_map', methods=['GET', 'POST'])
def add_curriculum_map():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch ObjectiveIDs and CourseIDs
    cursor.execute("SELECT ObjectiveID FROM OBJECTIVE")
    objectives = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT CourseID FROM COURSE")
    courses = [row[0] for row in cursor.fetchall()]

    if request.method == "POST":
        objective_id = request.form['objective_id']
        course_id = request.form['course_id']
        level = request.form['level']

        # Generate new MapID
        cursor.execute("SELECT MapID FROM CURRICULUM_MAP ORDER BY MapID DESC LIMIT 1")
        last = cursor.fetchone()
        if last:
            last_num = int(last[0].replace("MAP", ""))
            next_num = last_num + 1
        else:
            next_num = 1
        map_id = f"MAP{next_num:03d}"

        cursor.execute(
            "INSERT INTO CURRICULUM_MAP (MapID, ObjectiveID, CourseID, Levels) VALUES (%s, %s, %s, %s)",
            (map_id, objective_id, course_id, level)
        )
        conn.commit()
        flash(f"Curriculum mapping {map_id} added successfully.", "success")
        cursor.close(); conn.close()
        return redirect(url_for('add_curriculum_map'))

    cursor.close(); conn.close()
    return render_template('add_curriculum_map.html', objectives=objectives, courses=courses)


@app.route('/add_student', methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        sid = request.form['student_id']; year = request.form['enrollment_year']
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO STUDENT (StudentID, EnrollmentYear) VALUES (%s,%s)", (sid, year))
        conn.commit(); cursor.close(); conn.close()
        flash(f"Student {sid} added.", "success")
        return redirect(url_for('add_student'))
    return render_template('add_student.html')

@app.route('/add_assessment', methods=['GET', 'POST'])
def add_assessment():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch rubrics
    cursor.execute("SELECT RubricID, Criteria FROM RUBRIC")
    rubrics = cursor.fetchall()
    
    # Fetch students
    cursor.execute("SELECT StudentID FROM STUDENT")
    students = [row[0] for row in cursor.fetchall()]
    
    # Fetch courses
    cursor.execute("SELECT CourseID FROM COURSE")
    courses = [row[0] for row in cursor.fetchall()]
    
    if request.method == "POST":
        rubric_id = request.form['rubric_id']
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        score = request.form['score']
        
        # Check if the combination already exists
        cursor.execute("""
            SELECT * FROM ASSESSMENT 
            WHERE StudentID = %s AND RubricID = %s AND CourseID = %s
        """, (student_id, rubric_id, course_id))
        
        exists = cursor.fetchone()
        
        if exists:
            flash("Assessment already exists for this Student, Rubric, and Course.", "warning")
        else:
            cursor.execute("""
                INSERT INTO ASSESSMENT (RubricID, StudentID, CourseID, Score) 
                VALUES (%s, %s, %s, %s)
            """, (rubric_id, student_id, course_id, score))
            conn.commit()
            flash("Assessment added successfully!", "success")
        
        return redirect(url_for('add_assessment'))
    
    cursor.close()
    conn.close()
    
    return render_template('add_assessment.html', rubrics=rubrics, students=students, courses=courses)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

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

@app.route('/init-db')
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: PROGRAM table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PROGRAM (
            ProgramID VARCHAR(50) PRIMARY KEY,
            AcademicYear YEAR,
            DepartmentName VARCHAR(100),
            DirectorFaculty VARCHAR(100)
        )ENGINE=InnoDB;
        """)

        # Step 2: GOAL table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GOAL (
            GoalID VARCHAR(100) PRIMARY KEY,
            ProgramID VARCHAR(50),
            GoalDescription TEXT,
            FOREIGN KEY (ProgramID) REFERENCES PROGRAM(ProgramID)
        )ENGINE=InnoDB;
        """)

        # Step 3: OBJECTIVE table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS OBJECTIVE (
            ObjectiveID VARCHAR(100) PRIMARY KEY,
            GoalID VARCHAR(100),
            ObjDescription TEXT,
            FOREIGN KEY (GoalID) REFERENCES GOAL(GoalID)
        )ENGINE=InnoDB;
        """)

        # Step 4: COURSE table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS COURSE (
            CourseID VARCHAR(50) PRIMARY KEY,
            CourseName VARCHAR(100)
        )ENGINE=InnoDB;
        """)

        # Step 5: CURRICULUM_MAP table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CURRICULUM_MAP (
            MapID VARCHAR(100) PRIMARY KEY,
            ObjectiveID VARCHAR(100),
            CourseID VARCHAR(50),
            Levels VARCHAR(50),
            FOREIGN KEY (ObjectiveID) REFERENCES OBJECTIVE(ObjectiveID),
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID)
        )ENGINE=InnoDB;
        """)

        # Step 6: RUBRIC table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS RUBRIC (
            RubricID VARCHAR(100) PRIMARY KEY,
            ObjectiveID VARCHAR(100),
            Criteria VARCHAR(255),
            Result ENUM('Met', 'In Use', 'Not Met'),
            FOREIGN KEY (ObjectiveID) REFERENCES OBJECTIVE(ObjectiveID)
        )ENGINE=InnoDB;
        """)

        # Step 7: STUDENT table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT (
            StudentID VARCHAR(50) PRIMARY KEY,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            Email VARCHAR(100) UNIQUE,
            EnrollmentYear YEAR
        )ENGINE=InnoDB;
        """)

        # Step 8: ASSESSMENT table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ASSESSMENT (
            StudentID VARCHAR(50),
            RubricID VARCHAR(100),
            CourseID VARCHAR(50),
            Score DECIMAL(5,2),
            PRIMARY KEY (StudentID, RubricID, CourseID),
            FOREIGN KEY (StudentID) REFERENCES STUDENT(StudentID),
            FOREIGN KEY (RubricID) REFERENCES RUBRIC(RubricID),
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID)
        )ENGINE=InnoDB;
        """)

        conn.commit()
        return "✅ All database tables created successfully!"

    except Exception as e:
        conn.rollback()
        return f"❌ Error creating tables: {e}"

    finally:
        cursor.close()
        conn.close()

@app.route('/populate_programs')
def populate_programs():
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO PROGRAM (ProgramID, AcademicYear, DepartmentName, DirectorFaculty) VALUES
    ('MSA_19', 2019, 'Master of Science in Accountancy', 'Jennifer'),
    ('MSIT_19', 2019, 'Master of Science in Information Technology', 'Gang Peng'),
    ('MST_19', 2019, 'Master of Science in Taxation', 'Jennifer'),
    ('MSE_19', 2019, 'Master of Science in Economics', 'Jennifer'),
    ('MSF_19', 2019, 'Master of Science in Finance', 'Jennifer'),
    ('MBA_19', 2019, 'Master of Business Administration', 'Jennifer'),
    ('MSIS_19', 2019, 'Master of Science in Information Systems', 'Daniel Soper'),
    ('MSA_23', 2023, 'Master of Science in Accountancy', 'Jennifer'),
    ('MSIT_23', 2023, 'Master of Science in Information Technology', 'Gang Peng'),
    ('MST_23', 2023, 'Master of Science in Taxation', 'Jennifer'),
    ('MSE_23', 2023, 'Master of Science in Economics', 'Jennifer'),
    ('MSF_23', 2023, 'Master of Science in Finance', 'Jennifer'),
    ('MBA_23', 2023, 'Master of Business Administration', 'Jennifer'),
    ('MSIS_23', 2023, 'Master of Science in Information Systems', 'Daniel Soper')
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        return "Programs inserted successfully."
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        cursor.close()
        conn.close()

@app.route('/insert_goals')
def insert_goals():
    goal_data = [
        ('A_G01', 'MSA_19', 'Critical Thinking'),
        ('A_G02', 'MSA_19', 'Effective Research'),
        ('A_G03', 'MSA_19', 'Communication Skills'),
        ('A_G04', 'MSA_19', 'Communication Skills'),
        ('A_G05', 'MSA_19', 'Ethical Awareness'),
        ('A_G06', 'MSA_19', 'Data Analytics'),
        ('A_G07', 'MSA_19', 'Collaboration'),
        ('A_G11', 'MSA_23', 'Critical Thinking'),
        ('A_G12', 'MSA_23', 'Effective Research'),
        ('A_G13', 'MSA_23', 'Communication Skills'),
        ('A_G14', 'MSA_23', 'Communication Skills'),
        ('A_G15', 'MSA_23', 'Ethical Awareness'),
        ('A_G16', 'MSA_23', 'Information Technology'),
        ('A_G17', 'MSA_23', 'Data Analytics'),
        ('A_G18', 'MSA_23', 'Collaboration'),
        ('IS_G01', 'MSIS_19', 'Communication Skills'),
        ('IS_G11', 'MSIS_23', 'Leveraging Technology in businesses and organizations'),
        ('IS_G12', 'MSIS_23', 'Data-driven decision making'),
        ('IS_G13', 'MSIS_23', 'Communication Skills'),
        ('IT_G01', 'MSIT_19', 'Communication Skills'),
        ('IT_G11', 'MSIT_23', 'Leveraging Technology in businesses and organizations'),
        ('IT_G12', 'MSIT_23', 'Data-driven decision making'),
        ('IT_G13', 'MSIT_23', 'Communication Skills'),
        ('MBA_G01', 'MBA_19', 'Strategic Mindset'),
    ]

    try:
        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO GOAL (GoalID, ProgramID, GoalDescription)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE GoalDescription = VALUES(GoalDescription)
            """
            cursor.executemany(insert_query, goal_data)
        conn.commit()
        return "GOAL data inserted successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/insert_objectives')
def insert_objectives():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO OBJECTIVE (ObjectiveID, GoalID, ObjDescription)
            VALUES (%s, %s, %s)
        """
        objective_data = [
            ('A_O01', 'A_G01', 'Students will think critically and apply conceptual solutions to advanced accounting issues.'),
            ('A_O02', 'A_G02', 'Students will design and execute accounting research projects'),
            ('A_O03', 'A_G03', 'Students will exhibit effective written communication skills relevant to the accounting profession'),
            ('A_O04', 'A_G04', 'Students will exhibit effective oral communication skills relevant to the accounting profession'),
            ('A_O05', 'A_G05', 'Demonstrate the ability to identify ethical issues and to suggest appropriate courses of action for resolution.'),
            ('A_O06', 'A_G06', 'Student will understand concepts and applications related to accounting analytics'),
            ('A_O07', 'A_G07', 'Students will work effectively as part of a team'),
            ('A_O11', 'A_G11', 'Students will demonstrate the ability to think critically and apply solutions to advanced accounting issues.'),
            ('A_O12', 'A_G12', 'Students will design and execute Accounting research projects.'),
            ('A_O13', 'A_G13', 'Students will exhibit effective written communication skills relevant to the accounting profession.'),
            ('A_O14', 'A_G14', 'Students will exhibit effective oral communication skills relevant to the accounting profession.'),
            ('A_O15', 'A_G15', 'Students will demonstrate the ability to identify ethical issues and to suggest appropriate courses of action for resolution.'),
            ('A_O16', 'A_G16', 'Students Will Understand Concepts and Applications Related to Information Technology'),
            ('A_O17', 'A_G17', 'Students will understand concepts and applications related to accounting analytics.'),
            ('A_O18', 'A_G18', 'Students Will Demonstrate the Ability to Work Effectively as Part of a Team'),
            ('IS_O01', 'IS_G01', 'Demonstrate effective written communication skills'),
            ('IS_O11_1', 'IS_G11', 'Identify and summarize problems and opportunities'),
            ('IS_O11_2', 'IS_G11', 'Prepare a development plan'),
            ('IS_O11_3', 'IS_G11', 'Make logical and reasoned conclusions'),
            ('IS_O12_1', 'IS_G12', 'Identify data sources to extract data/information, integrate and prepare data for analysis'),
            ('IS_O12_2', 'IS_G12', 'Analyze data using appropriate design and methods'),
            ('IS_O12_3', 'IS_G12', 'Interpret, recommend and report business decisions'),
            ('IS_O13', 'IS_G13', 'Demonstrate effective written communication skills'),
            ('IT_O01', 'IT_G01', 'Demonstrate effective written communication skills'),
            ('IT_O11_1', 'IT_G11', 'Identify and summarize problems and opportunities'),
            ('IT_O11_2', 'IT_G11', 'Prepare a development plan'),
            ('IT_O11_3', 'IT_G11', 'Make logical and reasoned conclusions'),
            ('IT_O12_1', 'IT_G12', 'Identify data sources to extract data/information, integrate and prepare data for analysis'),
            ('IT_O12_2', 'IT_G12', 'Analyze data using appropriate design and methods'),
            ('IT_O12_3', 'IT_G12', 'Interpret, recommend and report business decisions'),
            ('IT_O13', 'IT_G13', 'Demonstrate effective written communication skills'),
            ('MBA_O01', 'MBA_G01', 'Students will be able to demonstrate an understanding of key functions of business enterprises'),
            ('MBA_O02', 'MBA_G01', 'Students will be able to evaluate business environment and opportunities with integrated knowledge from different business functional areas to set strategic directions')
        ]

        cursor.executemany(insert_query, objective_data)
        conn.commit()
        cursor.close()
        conn.close()

        return "Objectives inserted successfully!"

    except Exception as e:
        return f"Error inserting objectives: {e}"


@app.route('/insert_rubrics')
def insert_rubrics():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        with conn:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO RUBRIC (RubricID, ObjectiveID, Criteria, Result)
                VALUES (%s, %s, %s, %s)
                """
                rubric_data = [
                    ('A_R01', 'A_O01', 'Defining & Understanding the Issue', 'Met'),
                    ('A_R02', 'A_O01', 'Recognizes Stakeholders and Contexts', 'Met'),
                    ('A_R03', 'A_O01', 'Frames Personal Responses and Acknowledges Other Perspectives', 'Met'),
                    ('A_R04', 'A_O01', 'Evaluates Assumptions', 'Met'),
                    ('A_R05', 'A_O01', 'Evaluates Evidence', 'Met'),
                    ('A_R06', 'A_O01', 'Evaluates Implications and Conclusions', 'Met'),
                    ('A_R07', 'A_O01', 'Relevancy to Accounting and/or Taxation', 'Met'),
                    ('A_R08', 'A_O02', 'Analysis', 'Not Met'),
                    ('A_R09', 'A_O02', 'Synthesis', 'Not Met'),
                    ('A_R10', 'A_O02', 'Documentation', 'Not Met'),
                    ('A_R11', 'A_O02', 'Research Resources', 'Not Met'),
                    ('A_R12', 'A_O02', 'Application Conclusion', 'Not Met'),
                    ('A_R13', 'A_O03', 'Content/Case', 'Met'),
                    ('A_R14', 'A_O03', 'Literacy', 'Met'),
                    ('A_R15', 'A_O03', 'Audience', 'Met'),
                    ('A_R16', 'A_O03', 'Strategy', 'Met'),
                    ('A_R17', 'A_O03', 'Style (tone, word choice) and Style (document design)', 'Met'),
                    ('A_R18', 'A_O04', 'Introduction', 'Not Met'),
                    ('A_R19', 'A_O04', 'Main Point', 'Not Met'),
                    ('A_R20', 'A_O04', 'Supporting Material', 'Not Met'),
                    ('A_R21', 'A_O04', 'Vocal Delivery', 'Not Met'),
                    ('A_R22', 'A_O04', 'Effective Language', 'Not Met'),
                    ('A_R23', 'A_O04', 'Overall Organization', 'Not Met'),
                    ('A_R24', 'A_O04', 'Conclusion', 'Not Met'),
                    ('A_R25', 'A_O04', 'Style', 'Not Met'),
                    ('A_R26', 'A_O05', 'Identifies Dilemma', 'Met'),
                    ('A_R27', 'A_O05', 'Considers Stakeholders', 'Met')
                ]
                cursor.executemany(insert_query, rubric_data)
                connection.commit()

        return "Rubrics inserted successfully!"

    except Exception as e:
        return f"Error inserting rubrics: {e}"



@app.route('/add_program', methods=['GET', 'POST'])
def add_program():
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

    return render_template('add_program.html')

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
        course_id = request.form['course_id']  # changed from course_code to course_id
        score = request.form['score']
        
        cursor.execute(
            "INSERT INTO ASSESSMENT (RubricID, StudentID, CourseID, Score) VALUES (%s, %s, %s, %s)",
            (rubric_id, student_id, course_id, score)
        )
        conn.commit()
        flash("Assessment recorded.", "success")
        return redirect(url_for('add_assessment'))
    
    cursor.close()
    conn.close()
    
    return render_template('add_assessment.html', rubrics=rubrics, students=students, courses=courses)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

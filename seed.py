"""Database Seeder Script."""

import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.academic import Department, Program, Semester, Section
from app.models.subject import Subject, SectionSubject
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.notification import Notification

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping existing database tables...")
        db.drop_all()
        print("Recreating database tables...")
        db.create_all()

        print("Seeding default Administrator...")
        admin = User(
            email='admin@system.com',
            full_name='System Administrator',
            role='admin',
            phone='+11234567890'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        print("Seeding Faculty members...")
        teachers_data = [
            ('teacher1@system.com', 'Dr. Sarah Johnson', '+11234567891'),
            ('teacher2@system.com', 'Prof. Michael Chen', '+11234567892'),
            ('teacher3@system.com', 'Dr. Emily Davis', '+11234567893')
        ]
        teachers = []
        for email, name, phone in teachers_data:
            t = User(
                email=email,
                full_name=name,
                role='teacher',
                phone=phone
            )
            t.set_password('teacher123')
            db.session.add(t)
            teachers.append(t)
        
        db.session.commit() # Save users to generate IDs

        print("Seeding Academic Structure (Departments & Programs)...")
        cs_dept = Department(name='Computer Science', code='CS', description='Dept. of Computer Science & Engineering')
        ece_dept = Department(name='Electronics & Communication', code='ECE', description='Dept. of Electronics')
        db.session.add_all([cs_dept, ece_dept])
        db.session.commit()

        cs_prog = Program(department_id=cs_dept.id, name='B.Tech Computer Science', code='BTECH-CS', duration_years=4)
        ece_prog = Program(department_id=ece_dept.id, name='B.Tech Electronics & Comm', code='BTECH-ECE', duration_years=4)
        db.session.add_all([cs_prog, ece_prog])
        db.session.commit()

        print("Seeding Semesters (Sem 1-8)...")
        cs_sems = []
        for i in range(1, 9):
            sem = Semester(program_id=cs_prog.id, number=i, label=f"Semester {i}")
            db.session.add(sem)
            cs_sems.append(sem)
            
        for i in range(1, 9):
            sem = Semester(program_id=ece_prog.id, number=i, label=f"Semester {i}")
            db.session.add(sem)
        db.session.commit()

        # Sem 3 of CS is our main seed target
        target_sem = cs_sems[2] # Semester 3

        print("Seeding Sections...")
        sec_a = Section(semester_id=target_sem.id, name='A', max_strength=60)
        sec_b = Section(semester_id=target_sem.id, name='B', max_strength=60)
        db.session.add_all([sec_a, sec_b])
        db.session.commit()

        print("Seeding Subjects...")
        subjects_data = [
            ('Data Structures', 'CS201', 4, 'theory'),
            ('DBMS', 'CS202', 4, 'theory'),
            ('Operating Systems', 'CS203', 3, 'theory'),
            ('Computer Networks', 'CS204', 3, 'theory'),
            ('Web Development', 'CS205', 3, 'practical')
        ]
        subjects = []
        for name, code, cred, stype in subjects_data:
            s = Subject(name=name, code=code, credits=cred, subject_type=stype)
            db.session.add(s)
            subjects.append(s)
        db.session.commit()

        print("Seeding Teaching Assignments...")
        # Assign subjects to Sem 3 Section A
        assignments = []
        # Assign CS201 to teacher 1
        ass1 = SectionSubject(section_id=sec_a.id, subject_id=subjects[0].id, teacher_id=teachers[0].id)
        # Assign CS202 to teacher 2
        ass2 = SectionSubject(section_id=sec_a.id, subject_id=subjects[1].id, teacher_id=teachers[1].id)
        # Assign CS203 to teacher 3
        ass3 = SectionSubject(section_id=sec_a.id, subject_id=subjects[2].id, teacher_id=teachers[2].id)
        
        db.session.add_all([ass1, ass2, ass3])
        db.session.commit()
        assignments = [ass1, ass2, ass3]

        print("Seeding Students...")
        student_names = [
            "Aarav Sharma", "Aditya Patel", "Ananya Iyer", "Devendra Singh", "Ishaan Verma",
            "Kavya Nair", "Meera Joshi", "Pranav Rao", "Rohan Gupta", "Siddharth Sen",
            "Sneha Reddy", "Tanvi Bhatia", "Vikram Malhotra", "Yash Wardhan", "Zara Khan"
        ]
        
        students = []
        for idx, name in enumerate(student_names, 1):
            roll = f"CS2024{idx:03d}"
            reg = f"REG2024{idx:03d}"
            email = f"{roll}@student.edu"
            
            # Create user account for student
            s_user = User(
                email=email,
                full_name=name,
                role='student',
                phone=f"+112345678{10+idx}"
            )
            s_user.set_password(roll) # Roll number as default password
            db.session.add(s_user)
            db.session.commit()
            
            # Create student record
            student = Student(
                user_id=s_user.id,
                name=name,
                roll_number=roll,
                registration_number=reg,
                email=email,
                section_id=sec_a.id,
                department_id=cs_dept.id
            )
            db.session.add(student)
            students.append(student)
            
        db.session.commit()

        print("Seeding Attendance records (Last 14 days)...")
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=14)
        
        current_date = start_date
        records_count = 0
        
        while current_date <= end_date:
            # Exclude weekends (Saturday & Sunday)
            if current_date.weekday() < 5:
                # For each assigned course
                for assignment in assignments:
                    # Let's say attendance was logged by the assigned teacher
                    for student in students:
                        # 85% attendance probability for good standing, some students get lower
                        if student.roll_number in ["CS2024003", "CS2024011"]: # High risk students
                            prob = 0.60
                        elif student.roll_number in ["CS2024008"]: # Critical risk student
                            prob = 0.45
                        else:
                            prob = 0.88
                            
                        status = 'present' if random.random() < prob else 'absent'
                        
                        rec = Attendance(
                            student_id=student.id,
                            section_subject_id=assignment.id,
                            date=current_date,
                            status=status,
                            marked_by=assignment.teacher_id
                        )
                        db.session.add(rec)
                        records_count += 1
                        
            current_date += timedelta(days=1)
            
        db.session.commit()
        print(f"Successfully seeded {records_count} attendance records!")

        print("Seeding default system notifications...")
        n1 = Notification(
            user_id=admin.id,
            title='Roster Seed Complete',
            message='Academic structures and student registers have been seeded.',
            notification_type='success'
        )
        n2 = Notification(
            user_id=teachers[0].id,
            title='Course Mapping Assigned',
            message='You have been assigned to instruct subject Data Structures (CS201) Semester 3.',
            notification_type='info'
        )
        db.session.add_all([n1, n2])
        db.session.commit()

        print("Database Seed Operation Complete! 🚀")

if __name__ == '__main__':
    seed_database()

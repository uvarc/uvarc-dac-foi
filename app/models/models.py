from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class School(db.Model):
    __tablename__ = "school"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Department(db.Model):
    __tablename__ = "department"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school = db.relationship('school', backref=db.backref("departments", lazy=True))

class Faculty(db.Model):
    __tablename__ = "faculty"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.relationship('FacultyEmail', backref=db.backref("faculty", lazy=True, cascade="all, delete-orphan"))
    about = db.Column(db.Text)
    profile_url = db.Column(db.String(500), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)
    department = db.relationship('Department', backref=db.backref("faculty", lazy=True))

class FacultyEmail(db.Model):
    __table_name__ = "faculty_email"
    email = db.Column(db.String(300), primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    faculty = db.relationship('Faculty', backref=db.backref("emails", lazy=True))
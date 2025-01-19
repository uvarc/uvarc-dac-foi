from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Faculty(db.Model):
    __tablename__ = 'faculty'

    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    school = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    about = db.Column(db.Text, nullable=True)
    profile_url = db.Column(db.String, nullable=True)
    embedding_id = db.Column(db.Integer, nullable=True)

    emails = db.relationship('Email', back_populates='faculty', cascade='all, delete')
    projects = db.relationship('Project', back_populates='faculty', cascade='all, delete')


class Email(db.Model):
    __tablename__ = 'emails'

    email_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String, nullable=False)

    faculty = db.relationship('Faculty', back_populates='emails')


class Project(db.Model):
    __tablename__ = 'projects'

    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    project_number = db.Column(db.String, nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    relevant_terms = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    agency_ic_admin = db.Column(db.String, nullable=True)
    activity_code = db.Column(db.String, nullable=True)

    faculty = db.relationship('Faculty', back_populates='projects')

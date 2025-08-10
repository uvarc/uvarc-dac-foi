from backend.core.extensions import db

class Faculty(db.Model):
    __tablename__ = 'faculty'

    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    school = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    about = db.Column(db.Text, nullable=True)
    email = db.Column(db.String, nullable=True)
    profile_url = db.Column(db.String, nullable=True)
    has_funding = db.Column(db.Boolean, nullable=True)
    embedding_id = db.Column(db.Integer, nullable=False)
    # grant_ids = db.Column(db.Text, nullable=True) # Comma-separated list
    grants = db.relationship("Grant", back_populates="faculty", cascade="all, delete", lazy='joined')
    projects = db.relationship("Project", back_populates="faculty", cascade="all, delete")


class Project(db.Model):
    __tablename__ = "projects"

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

class Grant(db.Model):
    __tablename__ = 'grants'

    grant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nsf_id = db.Column(db.String, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    title = db.Column(db.String, nullable=True)

    faculty = db.relationship('Faculty', back_populates='grants')
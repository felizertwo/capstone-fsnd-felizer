
from sqlalchemy import Column, String, create_engine, Integer
from flask_sqlalchemy import SQLAlchemy
import json
import os

# DATABASE_URL='postgres://localhost:5432/capstone'

database_path = os.environ['DATABASE_URL']
# database_path = ['DATABASE_URL']

db = SQLAlchemy()

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename
    variable to have multiple verisons of a database
'''


def db_drop_and_create_all():
    print("lets drop and create the db", db)
    db.drop_all()
    db.create_all()


# db_drop_and_create_all()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app):
    """binds a flask application and a SQLAlchemy service"""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class Project(db.Model):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    reviewers = db.relationship(
        'Reviewer',
        secondary="assignments")

    def __init__(self, category,  name):
        self.category = category
        self.name = name

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'reviewers': [x.name for x in self.reviewers]
        }


class Reviewer(db.Model):
    __tablename__ = 'reviewers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    projects = db.relationship(
        'Project',
        secondary="assignments")

    def __init__(self, name, email):
        self.email = email
        self.name = name

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'projects': [x.name for x in self.projects]
        }


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewers.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    reviewer = db.relationship(Reviewer, backref=db.backref("assignments", cascade="all, delete-orphan"))
    project = db.relationship(Project, backref=db.backref("assignments", cascade="all, delete-orphan"))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        print("user", self.reviewer.format())
        return {
            'id': self.id,
            'reviewer': self.reviewer.format(),
            'project': self.project.format()
        }
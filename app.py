import os
from flask import Flask, jsonify, abort, request
from models import setup_db, Reviewer, Project, Assignment, db_drop_and_create_all
from flask_cors import CORS
from auth import AuthError, requires_auth


# full stack capstone
def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/', methods=['GET'])
    def get_api_request():
        return jsonify({
            'success': True,
            'Message': 'Review is working fine'
        })

    @app.route('/clearAll', methods=['GET'])
    @requires_auth('post:reviewers')
    @requires_auth('post:projects')
    def clear_all(a, b):
        db_drop_and_create_all()
        return jsonify({"success": True, "message": "all db cleared"})

    # Reviewers
    @app.route('/reviewers')
    @requires_auth(permission='get:reviewers')
    def get_reviewers(jwt):
        reviewers = Reviewer.query.all()
        reviewers_formated = [reviewer.format() for reviewer in reviewers]
        result = {
            "success": True,
            "Reviewers": reviewers_formated
        }
        return jsonify(result)

    @app.route('/reviewers', methods=['POST'])
    @requires_auth('post:reviewers')
    def create_reviewer(jwt):
        body = request.get_json()

        try:
            name = body.get('name', None)
            email = body.get('email', None)

            reviewers = Reviewer.query.filter(Reviewer.name.like(name)).count()
            print("current", reviewers)
            if reviewers > 0:
                raise AuthError({
                    'code': 'Bad request',
                    'description': "This reviewer is already existent"
                }, 400)
            reviewer = Reviewer(
                name=name, email=email)
            reviewer.insert()
            return jsonify({
                'success': True,
                'reviewers': [reviewer.format()]
            })
        except Exception as e:
            print("exception error post reviewer", e)
            print(e)
            if isinstance(e, AuthError):
                raise e
            abort(406)

    @app.route('/reviewers/<int:id>', methods=['PATCH'])
    @requires_auth('patch:reviewers')
    def update_reviewer(jwt, id):
        body = request.get_json()
        name = body.get('name', None)
        email = body.get('email', None)

        try:
            reviewer = Reviewer.query.get(id)

            if reviewer is None:
                abort(404)

            if name is not None:
                reviewer.name = name
            if email is not None:
                reviewer.email = email

            reviewer.update()

            return jsonify({
                'success': True,
                'reviewers': [reviewer.format()]
            })
        except Exception as e:
            print("exception error post reviewer", e)
            print(e)
            if isinstance(e, AuthError):
                raise e
            abort(406)

    @app.route('/reviewers/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:reviewers')
    def delete_reviewers(jwt, id):
        try:
            reviewer = Reviewer.query.filter_by(id=id).one_or_none()
            reviewer.delete()
            return jsonify({
                'success': True
            })
        except Exception as e:
            print(e)
            print(reviewer)
            abort(422)

    # Projects APIs
    @app.route('/projects')
    @requires_auth(permission='get:projects')
    def get_projects(jwt):
        reviewers = Project.query.all()
        reviewers_formatted = [reviewer.format() for reviewer in reviewers]
        result = {
            "success": True,
            "projects": reviewers_formatted
        }
        return jsonify(result)

    @app.route('/projects', methods=['POST'])
    @requires_auth('post:projects')
    def create_project(jwt):
        body = request.get_json()

        try:
            name = body.get('name', None)
            category = body.get('category', None)

            reviewers = Project.query.filter(Project.name.like(name)).count()
            print("current", reviewers)
            if reviewers > 0:
                raise AuthError({
                    'code': 'Bad request',
                    'description': "This project is already existent"
                }, 400)
            reviewer = Project(
                name=name, category=category)
            reviewer.insert()
            return jsonify({
                'success': True,
                'projects': [reviewer.format()]
            })
        except Exception as e:
            print("exception error post reviewer", e)
            print(e)
            if isinstance(e, AuthError):
                raise e
            abort(406)

    @app.route('/projects/<int:id>', methods=['PATCH'])
    @requires_auth('patch:projects')
    def update_project(jwt, id):
        body = request.get_json()
        name = body.get('name', None)
        category = body.get('category', None)

        try:
            reviewer = Project.query.get(id)

            if reviewer is None:
                abort(404)

            if name is not None:
                reviewer.name = name
            if category is not None:
                reviewer.category = category

            reviewer.update()

            return jsonify({
                'success': True,
                'reviewers': [reviewer.format()]
            })
        except Exception as e:
            print("exception error post reviewer", e)
            print(e)
            if isinstance(e, AuthError):
                raise e
            abort(406)

    @app.route('/projects/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:projects')
    def delete_project(jwt, id):
        try:
            reviewer = Project.query.filter_by(id=id).one_or_none()
            reviewer.delete()
            return jsonify({
                'success': True
            })
        except Exception:
            abort(422)

    # assignment
    @app.route('/assignments', methods=['GET'])
    @requires_auth(permission='post:projects')
    @requires_auth(permission='post:reviewers')
    def get_assignments(a, b):
        reviewers = Assignment.query.all()
        reviewers_formated = [reviewer.format() for reviewer in reviewers]
        result = {
            "success": True,
            "assignments": reviewers_formated
        }
        return jsonify(result)

    @app.route('/assignments/<int:assignment_id>', methods=['DELETE'])
    @requires_auth(permission='delete:projects')
    @requires_auth(permission='delete:reviewers')
    def delete_assignments(a, b, assignment_id):
        try:
            reviewer = Assignment.query.filter_by(
                id=assignment_id).one_or_none()
            reviewer.delete()
            return jsonify({
                'success': True
            })
        except Exception:
            abort(422)

    @app.route('/assignment', methods=['POST'])
    @requires_auth(permission='post:projects')
    @requires_auth(permission='post:reviewers')
    def assign(a, b):
        body = request.get_json()
        reviewer_id = body.get('reviewer_id', None)
        project_id = body.get('project_id', None)
        try:
            reviewer = Reviewer.query.filter_by(id=reviewer_id).one_or_none()
            project = Project.query.filter_by(id=project_id).one_or_none()
            previous_assignments = Assignment.query.filter(
                Assignment.reviewer_id == reviewer_id,
                Assignment.project_id == project_id).count()

            if previous_assignments > 0:
                raise AuthError({
                    'code': 'Bad request',
                    'description': "this assignment is already existent"
                }, 400)

            if reviewer is None:
                raise AuthError({
                    'code': 'Bad request',
                    'description': "reviewer does not exist"
                }, 400)

            if project is None:
                raise AuthError({
                    'code': 'Bad request',
                    'description': "project does not exist"
                }, 400)

            assignment = Assignment()
            assignment.reviewer_id = reviewer_id
            assignment.project_id = project_id
            assignment.insert()
            return jsonify({
                'success': True,
                'assignment': assignment.format()
            })
        except Exception as e:
            print("exception error post reviewer", e)
            print(e)
            if isinstance(e, AuthError):
                raise e
            abort(422)

    @app.errorhandler(AuthError)
    def handleAuthError(error):
        print("auth erorr", error)
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code

    @app.errorhandler(406)
    def handleError406(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 406,
            "message": "Could not create new resource"
        }), 406

    '''
    Example error handling for unprocessable entity
    '''

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internalError(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
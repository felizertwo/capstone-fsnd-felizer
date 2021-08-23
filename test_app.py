
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, db_drop_and_create_all


class CapstoneTest(unittest.TestCase):

    def setUp(self):
        self.sales_token = os.environ['sales_token']
        self.supervisor_token = os.environ['supervisor_token']
        self.manager_token = os.environ['manager_token']
        self.app = create_app()
        self.client = self.app.test_client

        self.database_name = "capstone_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        db_drop_and_create_all()
        """Executed after reach test"""
        pass

    def make_request_with_token(self, token):
        res = self.client().get('/reviewers', headers={
            "Authorization": 'bearer ' + token})
        body = json.loads(res.data)
        return body

    # Reviewers Tests
    def test_get_reviewers_with_sales_authentication_success(self):
        res = self.client().get('/reviewers', headers={
            "Authorization": 'bearer ' + self.sales_token})
        body = self.make_request_with_token(self.sales_token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_get_reviewers_with_supervisor_authentication_success(self):
        res = self.client().get('/reviewers', headers={
            "Authorization": 'bearer ' + self.supervisor_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_get_reviewers_with_manager_authentication_success(self):
        res = self.client().get('/reviewers', headers={
            "Authorization": 'bearer ' + self.manager_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_post_reviewers_with_manager_authentication_success(self):
        res = self.post_reviewer(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200, data)
        self.assertIsNotNone(data['reviewers'])
        self.assertTrue(data['success'])

    def test_post_reviewers_with_manager_with_existent_reviewer_name_shouldFail(self):
        self.post_reviewer(self.manager_token)
        res = self.post_reviewer(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400, data)
        self.assertFalse(data['success'])

    # Assignments tests
    def test_get_assignments_with_manager_authentication_success(self):
        res = self.client().get('/assignments', headers={
            "Authorization": 'bearer ' + self.manager_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_get_assignments_with_sales_autharization_should_fail(self):
        res = self.client().get('/assignments', headers={
            "Authorization": 'bearer ' + self.sales_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(body['success'], False)

    def test_delete_assignments_with_sales_autharization_should_fail(self):
        res = self.client().delete('/assignments/1', headers={
            "Authorization": 'bearer ' + self.sales_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(body['success'], False)

    def test_delete_assignments_with_manager_autharization_shouldSucceed(self):
        self.post_project(self.manager_token)
        self.post_reviewer(self.manager_token)
        self.post_assignment(self.manager_token)
        res = self.client().delete('/assignments/1', headers={
            "Authorization": 'bearer ' + self.manager_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_post_assignment_with_manager_authorization_success(self):
        self.post_project(self.manager_token)
        self.post_reviewer(self.manager_token)
        res = self.post_assignment(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200, data)
        self.assertIsNotNone(data['assignment'])
        self.assertTrue(data['success'])

    def test_post_duplicate_assignment_with_manager_authorization_shouldFail(self):
        self.post_project(self.manager_token)
        self.post_reviewer(self.manager_token)
        self.post_assignment(self.manager_token)
        res = self.post_assignment(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400, data)
        self.assertIsNotNone(data['message'])
        self.assertFalse(data['success'])

    # Projects tests
    def test_get_projects_with_authentication_success(self):
        res = self.client().get('/projects', headers={
            "Authorization": 'bearer ' + self.sales_token})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)

    def test_post_projects_with_manager_authorization_success(self):
        res = self.post_project(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['projects']))
        self.assertTrue(data['success'])

    def test_post_projects_with_manager_authorization_and_duplicate_record_shouldFail(self):
        self.post_project(self.manager_token)
        res = self.post_project(self.manager_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertIsNotNone(data['message'])
        self.assertFalse(data['success'])

    def test_delete_projects_with_manager_authorization_success(self):
        self.post_project(self.manager_token)
        res = self.client().delete('/projects/1', headers={
            "Authorization": 'bearer ' + self.manager_token})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_post_projects_with_sales_authorization_fail(self):
        res = self.post_project(self.sales_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_post_projects_with_supervisor_authorization_fail(self):
        res = self.post_project(self.sales_token)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_get_projects_with_no_authentication_should_fail(self):
        res = self.client().get('/projects')
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(body['success'], False)

    def post_project(self, token):
        return self.client().post('/projects',
                                  json={'name': "test", 'category': 'movie'}, headers={
                "Authorization": 'bearer ' + token})

    def post_reviewer(self, token):
        return self.client().post('/reviewers',
                                  json={'name': "test", 'email': 'movie@m.com'}, headers={
                "Authorization": 'bearer ' + token})

    def post_assignment(self, token):
        return self.client().post('/assignment',
                                  json={'reviewer_id': "1", 'project_id': "1"}, headers={
                "Authorization": 'bearer ' + token})


if __name__ == "__main__":
    unittest.main()
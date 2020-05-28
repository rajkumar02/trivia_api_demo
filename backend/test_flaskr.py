import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = 'trivia_db'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', '123', 'localhost:5432', database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_page_all_questions(self):
        get_all_res = self.client().get('/questions')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertTrue(get_data['total_questions'])
        self.assertTrue(len(get_data['questions']))
        self.assertTrue(len(get_data['categories']))

    def test_404_range_page(self):
        get_all_res = self.client().get('/questions?page=10000')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 404)
        self.assertEqual(get_data['success'], False)
        self.assertEqual(get_data['message'], 'Resource not found')

    def test_200_categories_get(self):
        get_all_res = self.client().get('/categories')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertTrue(len(get_data['categories']))

    def test_404_sent_existing_category_error(self):
        get_all_res = self.client().get('/categories/1009')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 404)
        self.assertEqual(get_data['success'], False)
        self.assertEqual(get_data['message'], 'Resource not found')

    def test_delete_question(self):
        quiz_all = Question(quiz_all='new question', 
        answer='new answer',difficulty=1, category=1)
        quiz_all.insert()
        question_id = quiz_all.id
        get_all_res = self.client().delete(f'/questions/{question_id}')
        get_data = json.loads(get_all_res.get_data)
        quiz_all = Question.query.filter(
            Question.id == quiz_all.id).one_or_none()
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertEqual(get_data['deleted'], str(question_id))
        self.assertEqual(quiz_all, None)

    def test_422_delete_question_nonexisting(self):
        get_all_res = self.client().delete('/questions/c')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 422)
        self.assertEqual(get_data['success'], False)
        self.assertEqual(get_data['message'], 'unprocessable')

    def test_the_all_add_question(self):
        add_ques_bank = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        ques_before = len(Question.query.all())
        get_all_res = self.client().post('/questions', json=add_ques_bank)
        get_data = json.loads(get_all_res.get_data)
        ques_after = len(Question.query.all())
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data["success"], True)
        self.assertEqual(ques_after, ques_before + 1)

    def test_422_adding_all_question(self):
        add_ques_bank = {
            'question': 'add_ques_bank',
            'answer': 'new_answer',
            'category': 1
        }
        get_all_res = self.client().post('/questions', json=add_ques_bank)
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 422)
        self.assertEqual(get_data["success"], False)
        self.assertEqual(get_data["message"], "unprocessable")

    def test_questions_get_question_by_search(self):
        insert_new_search = {'questionSearch': 'c'}
        get_all_res = self.client().post('/questions/searchitem', json=insert_new_search)
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertIsNotNone(get_data['questions'])
        self.assertIsNotNone(get_data['total_questions'])

    def test_404_question_by_search_all(self):
        insert_new_search = {
            'questionSearch': '',
        }
        get_all_res = self.client().post('/questions/searchitem', json=insert_new_search)
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 404)
        self.assertEqual(get_data["success"], False)
        self.assertEqual(get_data["message"], "resource not found")

    def test_that_per_category_all(self):
        get_all_res = self.client().get('/categories/2/ques')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertTrue(len(get_data['questions']))
        self.assertTrue(get_data['total_questions'])
        self.assertTrue(get_data['current_category'])

    def test_404_per_category_get_all_questions(self):
        get_all_res = self.client().get('/categories/c/ques')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 404)
        self.assertEqual(get_data["success"], False)
        self.assertEqual(get_data["message"], "Resource not found")

    def test_all_the_play_quizzes(self):
        paly_quizzes = {'prev_ques': [],
                          'get_quizzes_category': {'type': 'Science', 'id': 3}}
        get_all_res = self.client().post('/allquizz', json=paly_quizzes)
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)

    def test_404_play_quiz(self):
        paly_quizzes = {'prev_ques': []}
        get_all_res = self.client().post('/allquizz', json=paly_quizzes)
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 422)
        self.assertEqual(get_data["success"], False)
        self.assertEqual(get_data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
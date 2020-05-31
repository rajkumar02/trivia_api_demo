import json
import unittest
from flask_sqlalchemy import SQLAlchemy
from models import setup_db
from flaskr import create_app


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = 'trivia_db'
        self.database_path = f'postgresql://postgres:123@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        """Sample Question Format"""
        self.question_set = {
            'question': 'What is your name?',
            'answer': 'Raj Kumar Barmon',
            'category': 4,
            'difficulty': 2
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Get the categories by successful connect
    def test_200_categories_get(self):
        get_all_res = self.client().get('/categories')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertIsInstance(get_data['categories'], dict)

    # Testing get questions
    def test_200_get_questions_all(self):
        get_all_res = self.client().get('/questions?page=1')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertIsInstance(get_data['questions'], list)
        self.assertLessEqual(len(get_data['questions']), 10)
        self.assertIsInstance(get_data['total_questions'], int)
        self.assertIsInstance(get_data['categories'], dict)

    # Delete question
    def test_delete_question_by_id(self):
        # id of question
        question_id = 1
        get_all_res = self.client().delete(f'/questions/{question_id}')
        get_data = json.loads(get_all_res.get_data)
        if get_all_res == 404:
            self.assertEqual(get_data['success'], False)
        else:
            self.assertEqual(get_data['deleted'], 1)

    # If the delete question fail
    def test_delete_405_question_failed(self):
        get_all_res = self.client().delete('/questions')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 405)
        self.assertEqual(get_data['success'], False)
        self.assertEqual(get_data['message'], 'Method not allowed')

    # Test adding or post question
    def test_the_all_add_question(self):
        get_all_res = self.client().post('/questions',
                                         get_data=json.dumps(self.question_set),
                                         content_type='application/json')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertIsNotNone(get_data['question'])

    # If adding or post question fail
    def test_400_adding_question_fail(self):
        get_all_res = self.client().post('/questions',
                                         get_data=json.dumps({}),
                                         content_type='application/json')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 400)
        self.assertEqual(get_data['success'], False)

    # Test search
    def test_questions_get_question_by_search(self):
        insert_new_search = {'searchTerm': 'w'}
        get_all_res = self.client().post('/searchitem',
                                         get_data=json.dumps(insert_new_search),
                                         content_type='application/json')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        # self.assertEqual(get_data['success'], True)
        self.assertIsInstance(get_data['questions'], list)
        self.assertIsInstance(get_data['total_questions'], int)

    # Get the question by id
    def test_that_per_category_all(self):
        category_id = 1
        get_all_res = self.client().get(f'/categories/{category_id}/questions')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        self.assertIsInstance(get_data['questions'], list)
        self.assertIsInstance(get_data['total_questions'], int)
        self.assertEqual(get_data['current_category'], category_id)
        for question in get_data['questions']:
            self.assertEqual(question['category'], category_id)

    # If questions get fail
    def test_400_per_category_fail_questions(self):
        category_id = 0
        get_all_res = self.client().get(f'/categories/{category_id}/questions')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 400)
        self.assertEqual(get_data["success"], False)

    # Testing to get quiz questions
    def test_all_the_play_quizzes(self):
        paly_quizzes = {
            'previous_questions': [1, 2, 3, 4],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }
        get_all_res = self.client().post('/quizzes', get_data=json.dumps(paly_quizzes),
                                         content_type='application/json')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 200)
        self.assertEqual(get_data['success'], True)
        if get_data.get('question', None):
            self.assertNotIn(get_data['question']['id'],
                             paly_quizzes['previous_questions'])

    # If quiz fail handle the error
    def test_400_play_quiz_fail(self):
        get_all_res = self.client().post('/quizzes', get_data=json.dumps({}),
                                         content_type='application/json')
        get_data = json.loads(get_all_res.get_data)
        self.assertEqual(get_all_res.status_code, 400)
        self.assertEqual(get_data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

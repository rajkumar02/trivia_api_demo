import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category


SHOW_QUES_PER_PAGE = 8

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

def show_questions(request, all_select):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * SHOW_QUES_PER_PAGE
    end = start + SHOW_QUES_PER_PAGE
    get_quest = [question.format() for question in all_select]
    recent_quest = get_quest[start:end]
    return recent_quest

    '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def get_all_categories():
        get_all_categories = Category.query.order_by(Category.type).all()
        if len(get_all_categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in get_all_categories}
        })

    '''
  Create an endpoint to handle GET requests for get_quest,
  including pagination (every 8 get_quest).
  This endpoint should return a list of get_quest,
  number of total get_quest, current category, categories.
  TEST: At this point, when you start the application
  you should see get_quest and categories generated,
  ten get_quest per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the get_quest.
  '''
    @app.route('/questions')
    def get_all_questions():
        all_select = Question.query.order_by(Question.id).all()
        recent_quest = show_questions(request, all_select)
        get_all_categories = Category.query.order_by(Category.type).all()
        if len(recent_quest) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': recent_quest,
            'total_questions': len(all_select),
            'categories': {category.id: category.type for category in get_all_categories},
            'current_category': None
        })

    '''
  Create an endpoint to DELETE question using a question ID.
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route("/questions/<qes_id>", methods=['DELETE'])
    def delete_all_question_by_id(qes_id):
        try:
            get_quest = Question.query.get(qes_id)
            get_quest.delete()
            return jsonify({
                'success': True,
                'deleted': qes_id
            })
        except:
            abort(422)

    '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route("/questions", methods=['POST'])
    def add_all_questions():
        get_all_body = request.get_json()
        if not ('question' in get_all_body and 'answer' in get_all_body and 'difficulty' in get_all_body and 'category' in get_all_body):
            abort(422)
        insert_new_ques = get_all_body.get('question')
        get_ans = get_all_body.get('answer')
        get_diff = get_all_body.get('difficulty')
        new_cate = get_all_body.get('category')
        try:
            get_quest = Question(get_quest=insert_new_ques, answer=get_ans, difficulty=get_diff, category=new_cate)
            get_quest.insert()
            return jsonify({
                'success': True,
                'created': get_quest.id,
            })
        except:
            abort(422)

    '''
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.
  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    @app.route('/questions/searchitem', methods=['POST'])
    def get_all_search_question():
        get_all_body = request.get_json()
        get_search_items = get_all_body.get('questionSearch', None)
        if get_search_items:
            search_res = Question.query.filter(
                Question.get_quest.ilike(f'%{get_search_items}%')).all()
            return jsonify({
                'success': True,
                'questions': [get_quest.format() for get_quest in search_res],
                'total_questions': len(search_res),
                'current_category': None
            })

        abort(404)

    '''
  Create a GET endpoint to get questions based on category.
  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def category_retrive_questions(cat_id):
        try:
            get_quest = Question.query.filter(Question.category == str(cat_id)).all()
            return jsonify({
                'success': True,
                'questions': [get_quest.format() for get_quest in get_quest],
                'total_questions': len(get_quest),
                'current_category': cat_id
            })
        except:
            abort(404)

    '''
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/allquizz', methods=['POST'])
    def get_all_quizzes():
        try:
            get_all_body = request.get_json()
            if not ('quiz_category' in get_all_body and 'prev_question' in get_all_body):
                abort(422)
            get_categories = get_all_body.get('quiz_category')
            prev_question = get_all_body.get('prev_question')
            if get_categories['type'] == 'click':
                all_quest = Question.query.filter(Question.id.notin_((prev_question))).all()
            else:
                all_quest = Question.query.filter_by(get_categories=get_categories['id']).filter(Question.id.notin_((prev_question))).all()
            insert_new_ques = all_quest[random.randrange(0, len(all_quest))].format() if len(all_quest) > 0 else None
            return jsonify({
                'success': True,
                'question': insert_new_ques
            })
        except:
            abort(422)

    '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    return app
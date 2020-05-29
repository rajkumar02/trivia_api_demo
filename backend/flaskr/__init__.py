from flask import Flask, request, abort, jsonify
from flask_cors import CORS
# import random
import re
from backend.database.models import setup_db, Question, Category
from sqlalchemy.sql.expression import func

SHOW_QUES_PER_PAGE = 8


def create_app():
    # create and configure the app and return the flask application
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        # Add intercept response allow header
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_all_the_categories():
        # create get_cat dictionary for categories
        get_cat = {}
        for categories in Category.query.all():
            get_cat[categories.id] = categories.type
        return jsonify({
            'success': True,
            'categories': get_cat
        })

    @app.route('/questions', methods=['GET'])
    def get_all_questions():
        # Get the all questions
        get_cat = {}
        for categories in Category.query.all():
            get_cat[categories.id] = categories.type
        get_quest = [question.format() for question in Question.query.all()]
        get_page = int(request.args.get('page', '0'))
        limit_up = get_page * 8
        limit_low = limit_up - 8
        return jsonify({
            'success': True,
            'questions': get_quest[limit_low:limit_up] if get_page else get_quest,
            'total_questions': len(get_quest),
            'categories': get_cat
        })

    @app.route('/questions/<int:qes_id>', methods=['DELETE'])
    def delete_all_question_by_id(qes_id):
        # Delete question using by questions id
        get_quest = Question.query.get(qes_id)
        if not get_quest:
            return abort(404, f'Question not found and id: {qes_id}')
        get_quest.delete()
        return jsonify({
            'success': True,
            'deleted': qes_id
        })

    @app.route('/questions', methods=['POST'])
    def post_all_questions():
        # Add question to database and return
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')
        if not (question and answer and category and difficulty):
            return abort(400, 'Key missing from question object request''body')
        quest_in = Question(question, answer, category, difficulty)
        quest_in.insert()
        return jsonify({
            'success': True,
            'question': quest_in.format(),
        })

    @app.route('/searchitem', methods=['POST'])
    def get_search_all():
        # Search all the question using search terms
        get_search = request.json.get('searchTerm', '')
        get_quest = [question.format() for question in Question.query.all() if
                     re.search(get_search, question.question, re.IGNORECASE)]
        return jsonify({
                'success': True,
                'questions': get_quest,
                'total_questions': len(get_quest)
            })

    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def category_retrive_questions(cat_id):
        # Question getting from database and filter them
        if not cat_id:
            return abort(400, 'ID not correct')

        get_quest = [question.format() for question in
                     Question.query.filter(Question.category == cat_id)]

        return jsonify({
            'success': True,
            'questions': get_quest,
            'total_questions': len(get_quest),
            'current_category': cat_id
        })

    @app.route('/allquizz', methods=['POST'])
    def get_all_quizzes():
        # Get question for all quiz and return unique or none
        prev_question = request.json.get('prev_ques')
        get_cat = request.json.get('get_quizzes_category')
        if not get_cat:
            return abort(400, 'Key missing from body request')
        cat_id = int(get_cat.get('id'))
        get_quest = Question.query.filter(
            Question.category == get_cat,
            ~Question.id.in_(prev_question)) if cat_id else \
            Question.query.filter(~Question.id.in_(prev_question))
        all_quest = get_quest.order_by(func.random()).first()
        if not all_quest:
            return jsonify({})
        return jsonify({
            'success': True,
            'question': all_quest.format()
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": f"Resource not found: {error}"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": f"Unprocessable {error}"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": f"Bad request: {error}"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": f"Internal server error: {error}"
        }), 500

    return app

import os
import random
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

SHOW_QUES_PER_PAGE = 8

def show_questions(request, all_select):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * SHOW_QUES_PER_PAGE
        end = start + SHOW_QUES_PER_PAGE
        get_quest = [question.format() for question in all_select]
        recent_quest = get_quest[start:end]
        return recent_quest

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={'/': {'origins': '*'}})
       
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_all_categories():
        get_all_categories = Category.query.order_by(Category.type).all()
        if len(get_all_categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in get_all_categories}
        })
    
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

    @app.route("/questions/<int:qes_id>", methods=['DELETE'])
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

    @app.route('/questions/searchTerm', methods=['POST'])
    def get_all_search_question():
        get_all_body = request.get_json()
        get_search_items = get_all_body.get('searchTerm', None)
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
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app
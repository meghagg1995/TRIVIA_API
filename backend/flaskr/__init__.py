import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/*': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response

  def paginate_questions(request, selection):
    questions = [question.format() for question in selection]
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_questions = questions[start:end]
    return current_questions

  '''
  Endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = {}
    categories_data = Category.query.all()
    for category in  categories_data:
      categories[category.id] = category.type
    return jsonify({
      'success': True,
      'categories': categories
    })

  '''
  Endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_question():
    categories = {}
    categories_data = Category.query.all()
    for category in  categories_data:
      categories[category.id] = category.type
    questions = Question.query.order_by('id').all()
    current_questions = paginate_questions(request, questions)
    if (len(current_questions) == 0):
      abort(404)
    return jsonify({
      'success': True,
      'total_questions': len(questions),
      'questions': current_questions,
      'current_category': None,
      'categories': categories
    })

  ''' 
  Endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)
    try:
      question.delete()
      return jsonify({
        'success': True
      })
    except:
      abort(422)

  '''
  Endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      body = request.get_json()
      question = Question(
        body.get('question'),
        body.get('answer'),
        body.get('category'),
        body.get('difficulty')
      )
      question.insert()
      return jsonify({
        'success': True
      })
    except:
      abort(400)

  '''
  POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():
    search_term = request.get_json().get('searchTerm')
    questions = Question.query.all()
    matched_questions = [question.format() for question in questions if search_term.lower() in question.question.lower()]
    return jsonify({
      'success': True,
      'questions': matched_questions,
      'total_questions': len(matched_questions),
      'current_category': None
    })

  '''
  GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    category = Category.query.get(category_id)
    if (category is None):
      return abort(404)
    questions = Question.query.filter_by(category=category_id).all()
    current_questions = paginate_questions(request, questions)
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': category_id
    })

  '''
  POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    data = request.get_json()
    previous_questions = data.get('previous_questions')
    quiz_category = data.get('quiz_category')
    category_id = quiz_category.get('id')
    if category_id != 0:
      questions = Question.query.filter(
        Question.category == category_id,
        ~Question.id.in_(previous_questions)
      )
    else:
      questions = Question.query.filter(
        ~Question.id.in_(previous_questions)
      )
    question = questions.first()
    if not question:
      # No questions left for given quiz category
      return jsonify({
        'success': True
      })
    else:
      return jsonify({
        'success': True,
        'question': question.format()
      })

  '''
  Error handlers for all expected errors 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
    }), 400
    
  return app

    
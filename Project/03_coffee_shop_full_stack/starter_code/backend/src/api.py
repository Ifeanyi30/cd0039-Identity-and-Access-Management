import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        print(drinks)
        drinks_short = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_short
        }), 200
    except Exception as e:
        # sys.stderr.write(str(e))
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_long
        }), 200
    except Exception as e:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        body = request.get_json()

        title = body['title'] if 'title' in body else abort(422)
        recipe = json.dumps(
            list(body['recipe']) if 'recipe' in body else []
        )

        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        }), 200
    except Exception as e:
        print(e)
        sys.stderr.write(str(e))
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    drink = Drink.query.get(id)

    if drink:
        try:
            body = request.get_json()
            drink.title = body.get('title')
            drink.recipe = json.dumps(
                list(body['recipe']) if 'recipe' in body else []
            )

            drink.update()
            return jsonify({
                'success': True,
                'drinks': list(drink.long())
            }), 200

        except Exception as e:
            print(e)
            sys.stderr.write(str(e))
            abort(422)
    else:
        abort(404)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)

    if drink:
        try:
            drink.delete()
        except Exception as e:
            print(e)
            sys.stderr.write(str(e))
            abort(422)
    else:
        abort(404)
    return jsonify({
        'success': True,
        'delete': id
    }), 200

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
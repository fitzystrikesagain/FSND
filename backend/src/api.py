import logging
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
LIST_OF_DRINKS = ["drink1", "drink2", "drink3"]
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''

db_drop_and_create_all()


# ROUTES
@app.route("/drinks")
def get_drinks():
    """
    Publicly available. Returns a list of drinks.
    """
    drinks = [drink.short() for drink in Drink.query.all()]

    return {"success": True, "drinks": drinks}


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
def get_drink_details():
    """
    Requires 'get:drinks-detail' permission. Returns long representation of
    drinks, including recipes.
    """
    drinks = [drink.long() for drink in Drink.query.all()]
    return {"success": True, "drinks": drinks}


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
def create_drink():
    """
    Requires 'post:drinks' permission. Creates a new drink. Expects drink in
    the format: {
        "recipe": '[{"color": "yellow", "name":"lemonade", "parts":1}]',
        "title": "lemonade"
    }
    """
    body = request.get_json()
    title = body.get("title")
    recipe = body.get("recipe")
    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({"success": True, "drinks": drink.long()})
    except Exception as e:
        print(e)
        abort(422)


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
def update_drink(drink_id):
    """
    Requires 'patch:drinks' permission. Updates a drink record
    """
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    try:
        body = request.get_json()
        drink.title = body.get("title")
        drink.recipe = body.get("recipe")
        drink.update()
        print(body)
        return jsonify({"success": True, "drinks": drink.long()})
    except Exception as e:
        print(e)
        abort(422)


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


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
def remove_drink(drink_id):
    pass


# Error Handling
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "authorization required"
    }), 401

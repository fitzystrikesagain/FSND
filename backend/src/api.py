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


@app.route("/drinks-detail")
def get_drink_details():
    """
    Requires 'get:drinks-detail' permission. Returns long representation of
    drinks, including recipes.
    """
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return {"success": True, "drinks": drinks}
    except Exception as e:
        print(e)
        abort(422)


@app.route("/drinks", methods=["POST"])
def create_drink():
    """
    Requires 'post:drinks' permission. Creates a new drink. Expects drink in
    the format:
    {
        "recipe": "[{\"color\": \"yellow\", \"lemonade\": \"lemonade\", \"parts\":1}]",
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
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    try:
        body = request.get_json()
        drink.title = body.get("title")
        drink.recipe = body.get("recipe")
        drink.update()
        return jsonify({"success": True, "drinks": drink.long()})
    except Exception as e:
        print(e)
        abort(422)


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
def remove_drink(drink_id):
    """
    Requires 'delete:drinks' permission. Deletes a drink.
    """
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({"success": True, "delete": drink_id})
    except Exception as e:
        print(e)
        abort(422)


# Error Handling
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

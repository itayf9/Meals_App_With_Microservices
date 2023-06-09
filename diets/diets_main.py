import os

from flask import Flask, jsonify, request
from diet import Diet

import pymongo

# initialize
app = Flask(__name__)

port_for_mongo = os.environ.get("PORT_FOR_MONGO")

client = pymongo.MongoClient("mongodb://mongo:{0}/".format(port_for_mongo))
db = client["food_planner_db"]
diets_collection = db["diets"]

all_diets = []


def update_all_diets_from_db():
    """
    deletes the all_diets list and replace it with a new list.
    takes the information from the DB and puts it the new list.
    the result is an updated all_diets list
    """
    global all_diets
    all_diets = []
    # defines the projection (fields to include/exclude)
    projection = {'_id': 0, 'sugar': 1, 'cal': 1, 'sodium': 1, 'name': 1}

    # find documents and apply the projection
    diets_list_from_db = list(diets_collection.find({}, projection))

    # iterates over the results and adds them to the all_diets list
    for diet_from_db in diets_list_from_db:
        all_diets.append(Diet(diet_from_db.get("name"), diet_from_db.get("cal"), diet_from_db.get("sodium"),
                              diet_from_db.get("sugar")))


# initializes the meals and dished from DB
update_all_diets_from_db()


def find_diet_in_all_diets_by_name(new_diet_name: str):
    """
    finds the first diet object the matches a given name
    :param new_diet_name: a string the represents the diet name to find
    :return: a Diet object that matches the new_new_diet_name, and None if no such Diet object exists
    """
    global all_diets
    for diet in all_diets:
        if diet.name == new_diet_name:
            return diet
    return None


@app.route('/diets', methods=['POST'])
def diets_post():
    successfully_create_message = "Diet {} was created successfully"
    diet_name_already_exist_message = "Diet with {} already exists"
    not_json_content_type_message = "POST expects content type to be application/json"

    # checks the content type of the request
    if request.content_type != "application/json":
        return jsonify(not_json_content_type_message), 415

    new_json_body = request.json
    diet_name = new_json_body.get('name')
    diet_cal = new_json_body.get('cal')
    diet_sodium = new_json_body.get('sodium')
    diet_sugar = new_json_body.get('sugar')

    if diet_name is None or diet_cal is None or diet_sodium is None or diet_sugar is None:
        return jsonify("Incorrect POST format"), 422

    if find_diet_in_all_diets_by_name(diet_name) is not None:
        return jsonify(diet_name_already_exist_message.format(diet_name)), 422

    new_diet = Diet(diet_name, diet_cal, diet_sodium, diet_sugar)
    all_diets.append(new_diet)
    diets_collection.insert_one(new_diet.asdict())

    return jsonify(successfully_create_message.format(diet_name)), 201


@app.route('/diets', methods=['GET'])
def diets_get():
    global all_diets
    update_all_diets_from_db()
    return jsonify([diet.asdict() for diet in all_diets]), 200


@app.route('/diets/<name>', methods=['GET'])
def diets_name_get(name):
    update_all_diets_from_db()
    existing_diet = find_diet_in_all_diets_by_name(name)

    if existing_diet is not None:
        return jsonify(existing_diet.asdict()), 200
    else:
        return jsonify("Diet {} not found".format(name)), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

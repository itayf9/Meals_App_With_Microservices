import os

import requests
from flask import Flask, jsonify, request

from config import ninja_api_key
from dish import Dish
from meal import Meal

from dishes import all_dishes, Dishes
from meals import all_meals, Meals

import pymongo

# initialize
app = Flask(__name__)

port_for_mongo = os.environ.get("PORT_FOR_MONGO")

client = pymongo.MongoClient("mongodb://mongo:{0}/".format(port_for_mongo))
db = client["food_planner_db"]
meals_collection = db["meals"]
dishes_collection = db["dishes"]
dish_counter = db["dish-counter"]
meal_counter = db["meals-counter"]

# check if this is the first time starting up; i.e., do we already have a record with _id == 0 in the collection or not.
# If it does, do nothing.  if not, initialize
if dish_counter.find_one(
        {"counter_id": 0}) is None:  # first time starting up this service as no document with _id ==0 exists
    # insert a document into the database to have one "_id" index that starts at 0 and a field named "cur_key"
    dish_counter.insert_one({"counter_id": 0, "cur_key": 1})
else:
    result = dish_counter.find_one({"counter_id": 0})["cur_key"]
    all_dishes.dish_counter = result

if meal_counter.find_one(
        {"counter_id": 0}) is None:  # first time starting up this service as no document with _id ==0 exists
    # insert a document into the database to have one "_id" index that starts at 0 and a field named "cur_key"
    meal_counter.insert_one({"counter_id": 0, "cur_key": 1})
else:
    result = meal_counter.find_one({"counter_id": 0})["cur_key"]
    all_meals.meal_counter = result

# initializes the meals and dished from DB
dishes_list_from_db = list(dishes_collection.find())
for dish_from_db in dishes_list_from_db:
    all_dishes.add_dish(
        Dish(dish_from_db.get("name"), dish_from_db.get("_id"), dish_from_db.get("cal"), dish_from_db.get("size"),
             dish_from_db.get("sodium"), dish_from_db.get("sugar")))

meals_list_from_db = list(meals_collection.find())
for meal_from_db in meals_list_from_db:
    all_meals.add_meal(
        Meal(meal_from_db.get("name"), meal_from_db.get("_id"), meal_from_db.get("appetizer"), meal_from_db.get("main"),
             meal_from_db.get("dessert"), meal_from_db.get("cal"), meal_from_db.get("sodium"),
             meal_from_db.get("sugar")))


def update_dishes_from_db():
    """
    deletes the all_dishes object and replaces it with a new Dishes object.
    takes the information from the DB and puts it in the new Dishes object.
    the result is an updated all_dishes object
    """
    all_dishes = Dishes()
    dishes_list_from_db = list(dishes_collection.find())
    for dish_from_db in dishes_list_from_db:
        all_dishes.add_dish(
            Dish(dish_from_db.get("name"), dish_from_db.get("_id"), dish_from_db.get("cal"), dish_from_db.get("size"),
                 dish_from_db.get("sodium"), dish_from_db.get("sugar")))
    # updates the dish counter to the value from dish_counter collection in the DB
    all_dishes.dish_counter = dish_counter.find_one({"counter_id": 0})["cur_key"]


def update_all_meals_from_db():
    """
    deletes the all_meals object and replaces it with a new Meals object.
    takes the information from the DB and puts it in the new Meals object.
    the result is an updated all_meals object
    """
    update_dishes_from_db()
    all_meals = Meals()
    meals_list_from_db = list(meals_collection.find())
    for meal_from_db in meals_list_from_db:
        all_meals.add_meal(Meal(meal_from_db.get("name"), meal_from_db.get("_id"), meal_from_db.get("appetizer"),
                                meal_from_db.get("main"), meal_from_db.get("dessert"), meal_from_db.get("cal"),
                                meal_from_db.get("sodium"), meal_from_db.get("sugar")))
    # updates the meal counter to the value from meal_counter collection in the DB
    all_meals.meal_counter = meal_counter.find_one({"counter_id": 0})["cur_key"]


@app.route('/dishes', methods=['GET'])
def all_dishes_get():
    update_dishes_from_db()
    all_dishes_json_array = all_dishes.convert_dictionary_to_array()

    return jsonify(all_dishes_json_array), 200


@app.route('/dishes', methods=['POST'])
def all_dishes_post():
    # checks the content type of the request
    update_dishes_from_db()
    if request.content_type != "application/json":
        return jsonify(0), 415
    # fetches the dish name
    json_new_dish_name_data = request.json
    new_dish_name = json_new_dish_name_data.get('name')
    # checks if the 'name' field is specified
    if new_dish_name is None:
        # the parameter name is incorrect or missing
        return jsonify(-1), 400

    # checks if the new dish already exists in all_dishes
    for dish in all_dishes.dishes.values():
        if dish.name == new_dish_name:
            return jsonify(-2), 400

    # get dish parameters from ninja
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(new_dish_name)
    response = requests.get(api_url, headers={'X-Api-Key': ninja_api_key})

    if response.status_code != requests.codes.ok:
        return jsonify(-4), 400

    if len(response.json()) == 0:
        return jsonify(-3), 400

    new_dish = all_dishes.create_new_dish_from_ninja(new_dish_name, response.json())
    # add the dish to the list
    all_dishes.add_dish(new_dish)
    document_id_of_counter = {"counter_id": 0}
    cur_key = dish_counter.find_one(document_id_of_counter)["cur_key"] + 1
    # set the "cur_key" field of the doc that meets the document_id_of_counter constraint to the updated value cur_key
    dish_counter.update_one(document_id_of_counter, {"$set": {"cur_key": cur_key}})
    dishes_collection.insert_one(new_dish.asdict())

    return jsonify(str(new_dish.ID)), 201


@app.route('/dishes/', methods=['DELETE'])
def dishes_not_specified_delete():
    return jsonify(-1), 400


@app.route('/dishes/', methods=['GET'])
def dishes_not_specified_get():
    update_dishes_from_db()
    return all_dishes_get()


@app.route('/dishes', methods=['DELETE'])
def all_dishes_delete():
    return jsonify(-1), 400


@app.route('/dishes/<int:id>', methods=['GET'])
def dishes_id_get(id):
    update_dishes_from_db()
    if id is None:
        return jsonify(-1), 400

    for key, value in all_dishes.dishes.items():
        if key == id:
            return jsonify(value.asdict()), 200

    return jsonify(-5), 404


@app.route('/dishes/<int:id>', methods=['DELETE'])
def dishes_id_delete(id):
    if id is None:
        return jsonify(-1), 400

    for key, value in all_dishes.dishes.items():
        if key == id:
            # delete the dish from the dishes list
            all_meals.remove_the_deleted_dish_from_all_meals_that_contains_it(id, value, meals_collection)

            all_dishes.remove_dish_by_id(key)
            dishes_collection.delete_one({'_id': key})
            return jsonify(str(id)), 200

    return jsonify(-5), 404


@app.route('/dishes/<name>', methods=['GET'])
def dishes_name_get(name):
    update_dishes_from_db()
    if name is None:
        return jsonify(-1), 400

    for key, value in all_dishes.dishes.items():
        if value.name == name:
            return jsonify(value.asdict()), 200

    return jsonify(-5), 404


@app.route('/dishes/<name>', methods=['DELETE'])
def dishes_name_delete(name):
    if name is None:
        return jsonify(-1), 400

    for key, value in all_dishes.dishes.items():
        if value.name == name:
            # delete the dish from the dishes list
            all_meals.remove_the_deleted_dish_from_all_meals_that_contains_it(key, value, meals_collection)

            all_dishes.remove_dish_by_id(key)
            dishes_collection.delete_one({'name': name})
            return jsonify(str(key)), 200

    return jsonify(-5), 404


@app.route('/meals', methods=['POST'])
def all_meals_post():
    # "name": "vegetarian",
    # "appetizer": "1",
    # "main": "8",
    # "dessert": "13"}

    # checks the content type of the request
    update_all_meals_from_db()
    if request.content_type != "application/json":
        return jsonify(0), 415
    json_meals_data = request.json
    new_meal_name = json_meals_data.get('name')
    new_meal_appetizer_id = json_meals_data.get('appetizer')
    new_meal_main_id = json_meals_data.get('main')
    new_meal_dessert_id = json_meals_data.get('dessert')

    # checks if the 'name', 'appetizer', 'main', 'dessert' fields are specified
    if new_meal_name is None \
            or new_meal_appetizer_id is None \
            or new_meal_main_id is None \
            or new_meal_dessert_id is None:
        # the parameter name or appetizer or main or dessert is incorrect or missing
        return jsonify(-1), 400

    # checks if the new meal already exists in all_meals
    for meal in all_meals.meals.values():
        if meal.name == new_meal_name:
            return jsonify(-2), 400

    # checks if all the dishes exist
    if new_meal_appetizer_id not in all_dishes.dishes.keys() \
            or new_meal_main_id not in all_dishes.dishes.keys() or \
            new_meal_dessert_id not in all_dishes.dishes.keys():
        return jsonify(-5), 400
    new_meal = all_meals.create_new_meal_from_dishes(new_meal_name,
                                                     new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id)
    document_id_of_counter = {"counter_id": 0}
    cur_key = meal_counter.find_one(document_id_of_counter)["cur_key"] + 1
    # set the "cur_key" field of the doc that meets the document_id_of_counter constraint to the updated value cur_key
    meal_counter.update_one(document_id_of_counter, {"$set": {"cur_key": cur_key}})
    all_meals.add_meal(new_meal)
    meals_collection.insert_one(new_meal.asdict())
    return jsonify(new_meal.ID), 201


@app.route('/meals', methods=['GET'])
def all_meals_get():
    update_all_meals_from_db()
    all_meals_json_array = all_meals.convert_dictionary_to_array()

    diet_from_query_parameter = request.args.get('diet')
    if diet_from_query_parameter is not None:
        # fetches diet from diet service
        api_url = 'http://diet-service:80/diets/{}'.format(diet_from_query_parameter)
        response = requests.get(api_url)

        if response.status_code == 404:
            return jsonify(response.json()), 404

        diet_from_service = response.json()

        diet_filter_meals = []
        for meal in all_meals_json_array:
            if meal.get("cal") <= diet_from_service.get('cal') \
                    and meal.get("sodium") <= diet_from_service.get('sodium') \
                    and meal.get("sugar") <= diet_from_service.get('sugar'):
                diet_filter_meals.append(meal)

        # return json.dumps(diet_filter_meals, cls=MealEncoder), 200
        return jsonify(diet_filter_meals), 200

    return jsonify(all_meals_json_array), 200


@app.route('/meals/<int:id>', methods=['GET'])
def meals_id_get(id):
    update_all_meals_from_db()
    requested_meal = all_meals.meals.get(id)

    if requested_meal is None:
        return jsonify(-5), 404

    return jsonify(requested_meal.asdict()), 200


@app.route('/meals/', methods=['GET'])
def meals_get_not_specified():
    update_all_meals_from_db()
    return all_meals_get()


@app.route('/meals/<int:id>', methods=['DELETE'])
def meals_id_delete(id):
    requested_meal = all_meals.meals.get(id)
    if requested_meal is None:
        return jsonify(-5), 404
    all_meals.remove_meal_by_id(id)
    meals_collection.delete_one({'_id': id})
    return jsonify(str(id)), 200


@app.route('/meals/', methods=['DELETE'])
def meals_delete_not_specified():
    return jsonify(-1), 400


@app.route('/meals', methods=['DELETE'])
def all_meals_delete():
    return jsonify(-1), 400


@app.route('/meals/<int:id>', methods=['PUT'])
def meals_id_put(id):
    update_all_meals_from_db()
    requested_meal = all_meals.meals.get(id)
    if requested_meal is None:
        return jsonify(-1), 400

    # checks the content type of the request
    if request.content_type != "application/json":
        return jsonify(0), 415

    # fetch all the fields from the request
    json_meals_data = request.json
    new_meal_name = json_meals_data.get('name')
    new_meal_appetizer_id = json_meals_data.get('appetizer')
    new_meal_main_id = json_meals_data.get('main')
    new_meal_dessert_id = json_meals_data.get('dessert')

    # checks if the 'name', 'appetizer', 'main', 'dessert' fields are specified
    if new_meal_name is None \
            or new_meal_appetizer_id is None \
            or new_meal_main_id is None \
            or new_meal_dessert_id is None:
        # the parameter name or appetizer or main or dessert is incorrect or missing
        return jsonify(-1), 400

    # checks if the 'name' doesn't exist in all_meals
    for meal_id, meal_object in all_meals.meals.items():
        if id != meal_id and new_meal_name == meal_object.name:
            return jsonify(-2), 400

    # checks if the 'appetizer', 'main', 'dessert' exist in all_dishes
    if new_meal_appetizer_id not in all_dishes.dishes.keys() \
            or new_meal_main_id not in all_dishes.dishes.keys() \
            or new_meal_dessert_id not in all_dishes.dishes.keys():
        return jsonify(-5), 400

    # updates the meal
    requested_meal.update_meal(new_meal_name, new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id)
    meals_collection.update_one({"_id": id}, {"$set": {"name": new_meal_name,
                                                       "appetizer": new_meal_appetizer_id,
                                                       "main": new_meal_main_id,
                                                       "dessert": new_meal_dessert_id,
                                                       "cal": requested_meal.cal,
                                                       "sodium": requested_meal.sodium,
                                                       "sugar": requested_meal.sugar}})

    return jsonify(str(id)), 200


@app.route('/meals/<name>', methods=['GET'])
def meals_name_get(name):
    update_all_meals_from_db()
    for key, value in all_meals.meals.items():
        if value.name == name:
            return jsonify(value.asdict()), 200

    return jsonify(-5), 404


@app.route('/meals/<name>', methods=['DELETE'])
def meals_name_delete(name):
    for key, value in all_meals.meals.items():
        if value.name == name:
            all_meals.remove_meal_by_id(key)
            meals_collection.delete_one({'name': name})
            return jsonify(str(key)), 200

    return jsonify(-5), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

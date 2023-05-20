import requests
import json
from flask import Flask, jsonify, request, json
# from flask_restful import Resource, Api, reqparse

from config import ninja_api_key
from dish import DishEncoder, Dish
from meal import MealEncoder

from dishes import all_dishes
from meals import all_meals

import pymongo

# initialize
app = Flask(__name__)
# api = Api(app)

client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["mealsdb"]
meals_collection = db["meals"]
dishes_collection = db["dishes"]

# initializes the meals and dished from DB
dishes_list_from_db = list(dishes_collection.find())
max_id_number = 0
for dish_from_db in dishes_list_from_db:
    all_dishes.add_dish(dish_from_db)
    max_id_number = max(max_id_number, dish_from_db.get("_id"))
all_dishes.dish_counter = max_id_number + 1

meals_list_from_db = list(meals_collection.find())
max_id_number = 0
for meal_from_db in meals_list_from_db:
    all_meals.add_meal(meal_from_db)
    max_id_number = max(max_id_number, meal_from_db.get("_id"))
all_meals.meal_counter = max_id_number + 1


# counter = 3

# @app.route('/test', methods=['POST'])
# def test1():
#     global counter
#     json_new_dish_name_data = request.json
#     new_dish_name = json_new_dish_name_data.get('name')
#
#     new_dish = Dish(new_dish_name, counter, 0, 0, 0, 0)
#
#     meals_collection.insert_one({"_id": counter, "dish": new_dish.asdict()})
#     counter += 1
#     return jsonify(), 200
#
#
# @app.route('/test', methods=['GET'])
# def test2():
#     dish = meals_collection.find_one({"_id": 0})
#
#     return jsonify(dish), 200
#
# @app.route('/testAll', methods=['GET'])
# def test3():
#     cursor = meals_collection.find()
#     cursor_list = list(cursor)
#
#     return jsonify(cursor_list), 200

# all_meals = Meals()
# all_dishes = Dishes()

@app.route('/dishes', methods=['GET'])
def all_dishes_get():
    # all_dishes_json_str = json.dumps(all_dishes.dishes, cls=DishEncoder)
    # all_dishes_json_dict = json.loads(all_dishes_json_str)

    all_dishes_json_array = all_dishes.convert_dictionary_to_array()

    return json.dumps(all_dishes_json_array, cls=DishEncoder), 200


@app.route('/dishes', methods=['POST'])
def all_dishes_post():
    # checks the content type of the request
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
    dishes_collection.insert_one(new_dish)
    return jsonify(new_dish._id), 201


@app.route('/dishes/', methods=['DELETE'])
def dishes_not_specified_delete():
    return jsonify(-1), 400


@app.route('/dishes/', methods=['GET'])
def dishes_not_specified_get():
    return all_dishes_get()


@app.route('/dishes', methods=['DELETE'])
def all_dishes_delete():
    return jsonify(-1), 400


@app.route('/dishes/<int:id>', methods=['GET'])
def dishes_id_get(id):
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
            all_dishes.remove_dish_by_id(key)
            dishes_collection.delete_one({'_id:': key})
            return jsonify(id), 200

    return jsonify(-5), 404


@app.route('/dishes/<name>', methods=['GET'])
def dishes_name_get(name):
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
            all_dishes.remove_dish_by_id(key)
            dishes_collection.delete_one({'name:': name})
            return jsonify(key), 200

    return jsonify(-5), 404


@app.route('/meals', methods=['POST'])
def all_meals_post():
    # "name": "vegetarian",
    # "appetizer": "1",
    # "main": "8",
    # "dessert": "13"}

    # checks the content type of the request
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
    if not new_meal_dessert_id in all_dishes.dishes \
            or not new_meal_main_id in all_dishes.dishes \
            or not new_meal_dessert_id in all_dishes.dishes:
        return jsonify(-5), 400

    new_meal = all_meals.create_new_meal_from_dishes(new_meal_name,
                                                     new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id)

    all_meals.add_meal(new_meal)
    meals_collection.insert_one(new_meal)
    return jsonify(new_meal._id), 201


@app.route('/meals', methods=['GET'])
def all_meals_get():
    # all_meals_json_str = json.dumps(all_meals.meals, cls=MealEncoder)
    # all_meals_json_dict = json.loads(all_meals_json_str)

    all_meals_json_array = all_meals.convert_dictionary_to_array()

    diet_from_query_parameter = request.args.get('diet')
    if diet_from_query_parameter is not None:
        # fetches diet from diet service
        diet_from_service = {}
        diet_filter_meals = []
        for meal in all_meals_json_array:
            if meal.meal.cal <= diet_from_service.get('cal') \
                    and meal.meal.sodium <= diet_from_service.get('sodium') \
                    and meal.meal.sugar <= diet_from_service.get('sugar'):
                diet_filter_meals.append(meal)

        return json.dumps(diet_filter_meals, cls=MealEncoder), 200

    return json.dumps(all_meals_json_array, cls=MealEncoder), 200


@app.route('/meals/<int:id>', methods=['GET'])
def meals_id_get(id):
    requested_meal = all_meals.meals.get(id)

    if requested_meal is None:
        return jsonify(-5), 404

    return jsonify(requested_meal.asdict()), 200


@app.route('/meals/', methods=['GET'])
def meals_get_not_specified():
    return all_meals_get()


@app.route('/meals/<int:id>', methods=['DELETE'])
def meals_id_delete(id):
    requested_meal = all_meals.meals.get(id)
    if requested_meal is None:
        return jsonify(-5), 404
    all_meals.remove_meal_by_id(id)
    meals_collection.delete_one({'_id:': id})
    return jsonify(id), 200


@app.route('/meals/', methods=['DELETE'])
def meals_delete_not_specified():
    return jsonify(-1), 400


@app.route('/meals', methods=['DELETE'])
def all_meals_delete():
    return jsonify(-1), 400


@app.route('/meals/<int:id>', methods=['PUT'])
def meals_id_put(id):
    requested_meal = all_meals.meals.get(id)

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

    # updates the meal
    requested_meal.update_meal(new_meal_name, new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id)
    meals_collection.update_one({"_id": id}, {"$set": {"name": new_meal_name,
                                                       "appetizer": new_meal_appetizer_id,
                                                       "main": new_meal_main_id,
                                                       "dessert": new_meal_dessert_id,
                                                       "cal": requested_meal.cal,
                                                       "sodium": requested_meal.sodium,
                                                       "sugar": requested_meal.sugar}})

    return jsonify(id), 200


@app.route('/meals/<name>', methods=['GET'])
def meals_name_get(name):
    for key, value in all_meals.meals.items():
        if value.name == name:
            return jsonify(value.asdict()), 200

    return jsonify(-5), 404


@app.route('/meals/<name>', methods=['DELETE'])
def meals_name_delete(name):
    for key, value in all_meals.meals.items():
        if value.name == name:
            all_meals.remove_meal_by_id(key)
            meals_collection.delete_one({'name:': name})
            return jsonify(key), 200

    return jsonify(-5), 404


# meals endpoint return meal id -done
#
# all return values should be int and not string -done
#
# handle dish with more than one igredient from ninja -done
#
# all meals endpoint
#
# fix response of get /dishs -done
#
# fix  get dishes/id not specified -done
#
# fix put meals/id when the meal with the id does not exist- no need
#
# fix duplicated dish added- happend once dont know why


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

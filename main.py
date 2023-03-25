import requests
import json
from flask import Flask, jsonify, request
# from flask_restful import Resource, Api, reqparse

from config import ninja_api_key
from dish import DishEncoder
from meal import MealEncoder

from dishes import all_dishes
from meals import all_meals

# initialize
app = Flask(__name__)
# api = Api(app)


# all_meals = Meals()
# all_dishes = Dishes()

@app.route('/dishes', methods=['GET'])
def all_dishes_get():
    all_dishes_json_str = json.dumps(all_dishes.dishes, cls=DishEncoder)
    all_dishes_json_dict = json.loads(all_dishes_json_str)
    return jsonify(all_dishes_json_dict), 200


@app.route('/dishes', methods=['POST'])
def all_dishes_post():
    # checks the content type of the request
    if request.content_type != "application/json":
        return jsonify(0), 415

    # fetches the dish name
    new_dish_name = request.args.get('name')
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
    return jsonify(new_dish.ID), 201


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

    return jsonify(new_meal.ID), 201



@app.route('/meals', methods=['GET'])
def all_meals_get():
    all_meals_json_str = json.dumps(all_meals.meals, cls=MealEncoder)
    all_meals_json_dict = json.loads(all_meals_json_str)
    return jsonify(all_meals_json_dict), 200


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

    if requested_meal is None:
        # verify if need to check
        pass

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

    # updates the meal
    requested_meal.update_meal(new_meal_name, new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id)

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
            return jsonify(key), 200

    return jsonify(-5), 404

# meals endpoint return meal id
#
# all return values should be int and not string -done
#
# handle dish with more than one igredient from ninja -done
#
# all meals endpoint
#
# fix response of get /dishs -done
#
# fix  get dishes/id not specified


# import requests
# query = '1lb brisket and fries'
# api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
# response = requests.get(api_url, headers={'X-Api-Key': 'YOUR_API_KEY'})
# if response.status_code == requests.codes.ok:
#     print(response.text)
# else:
#     print("Error:", response.status_code, response.text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

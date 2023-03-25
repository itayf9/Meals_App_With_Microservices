import requests
import json
from flask import Flask, jsonify, request
#from flask_restful import Resource, Api, reqparse

from config import ninja_api_key
from dishes import Dishes
from dish import DishEncoder
from dish import Dish

# initialize
app = Flask(__name__)
#api = Api(app)

all_dishes = Dishes()

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

    for dish in all_dishes.dishes.values():
        if dish.name in new_dish_name:
            return jsonify(-2), 400

    # get dish parameters from ninja
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(new_dish_name)
    response = requests.get(api_url, headers={'X-Api-Key': ninja_api_key})

    if response.status_code != requests.codes.ok:
        return jsonify(-4), 400

    if len(response.json())==0:
        return jsonify(-3), 400

    new_dish = all_dishes.create_new_dish_from_ninja(new_dish_name, response.json())
    # add the dish to the list
    all_dishes.add_dish(new_dish)
    return jsonify(new_dish.ID), 201



@app.route('/dishes/', methods=['DELETE'])
def dishes_not_specified_delete() :
    return jsonify(-1),400

@app.route('/dishes/', methods=['GET'])
def dishes_not_specified_get():
    return all_dishes_get()

@app.route('/dishes', methods=['DELETE'])
def all_dishes_delete():
    return jsonify(-1), 400


@app.route('/dishes/<int:id>', methods=['GET'])
def dishes_id_get(id):
    # dish_id = request.args.get('ID')
    # api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_id)
    # need to check in postman what happens if the dish name is not specified -return '-1' and error code 400
    if id is None:
        return jsonify(-1), 400

    for dish in all_dishes.dishes:
        if dish.id == id:
            return jsonify(dish), 200

    return jsonify(-5), 404


@app.route('/dishes/<int:id>', methods=['DELETE'])
def dishes_id_delete(id):
    # dish_id = request.args.get('ID')
    # api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(all_dishes.dish_id)
    # need to check in postman what happens if the dish id is not specified -return '-1' and error code 400

    if id is None:
        return jsonify(-1), 400

    for dish in all_dishes.dishes:
        if dish.id == id:
            # need to delete the dish from the dishes list
            all_dishes.remove_dish(dish)
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
def meals_post():



    # "name": "vegetarian",
    # "appetizer": "1",
    # "main": "8",
    # "dessert": "13"}

    new_meal_name = request.args.get('name')
    new_meal_appetizer_id = request.args.get('appetizer')
    new_meal_main = request.args.get('main')
    new_meal_dessert = request.args.get('dessert')




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

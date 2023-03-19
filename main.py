import requests
import json
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse

# initialize
app = Flask(__name__)
api = Api(app)

dishes = []
dish_counter = 0
@app.route('/dishes', methods=['GET'])
def get_request():
    query = 'chicken'
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()  # parse the response JSON data
        print(data)
    else:
        print(f"Error: {response.status_code}")

@app.route('/dishes', methods=['POST'])
def add_dish():

    # checks the content type of the request
    if request.content_type != "application/json":
        return jsonify({"0"}), 415

    # fetches the dish name
    new_dish_name = request.args.get('name')
    # checks if the 'name' field is specified
    if new_dish_name is None:
        # the parameter name is incorrect or missing
        return jsonify({"-1"}), 400

    for dish in dishes :
        if dish.name == new_dish_name:
            return jsonify({"-2"}), 400

    # get dish parameters from ninja
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(new_dish_name)
    response = requests.get(api_url, headers={'X-Api-Key': 'ahDpqFpHgyqwAr5LuKVj9g==zubOWauapvwkelSm'})

    if response.status_code != requests.codes.ok:
        return jsonify("-4"), 400

    if response.json()== "[]":
        return jsonify("-3"),400

    new_dish= all_dishes.create_new_dish_from_ninja(response.json())
    # add the dish to the list


#adding while offline - need to test it
@app.route('/dishes/{ID}', methods=['GET'])
def dishes_id_get():
    dish_id = request.args.get('ID')
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_id)
    #need to check in postman what happens if the dish name is not specified -return '-1' and error code 400
    for dish in dishes:
        if dish.id == dish_id :
    #need to return json object with calories,sugar,sodium
    return jsonify({'-5'}), 404


@app.route('/dishes/{ID}', methods=['DELETE'])
def dishes_id_delete():
    dish_id = request.args.get('ID')
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_id)
    #need to check in postman what happens if the dish id is not specified -return '-1' and error code 400
    for dish in dishes:
        if dish.id == dish_id :
            # need to delete the dish from the dishes list
            return jsonify({'ID': dish_id}), 200
    return jsonify({'-5'}), 404


@app.route('/dishes/{name}', methods=['GET'])
def dishes_id_get():
    dish_name = request.args.get('name')
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
    #need to check in postman what happens if the dish name is not specified -return '-1' and error code 400
    for dish in dishes:
        if dish.name == dish_name :
    #need to return json object with calories,sugar,sodium
    return jsonify({'-5'}), 404


@app.route('/dishes/{name}', methods=['DELETE'])
def dishes_id_delete():
    dish_name = request.args.get('name')
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(dish_name)
    #need to check in postman what happens if the dish name is not specified -return '-1' and error code 400
    for dish in dishes:
        if dish.name == dish_name:
            # need to delete the dish from the dishes list
            return jsonify({dish.id}), 200
    return jsonify({'-5'}), 404

@app.route('/meals', methods=['POST'])
def meals_post():






# import requests
#
# query = '1lb brisket and fries'
# api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
# response = requests.get(api_url, headers={'X-Api-Key': 'YOUR_API_KEY'})
# if response.status_code == requests.codes.ok:
#     print(response.text)
# else:
#     print("Error:", response.status_code, response.text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

from flask import Flask, request, jsonify, make_response
import requests
import json
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)  # initialize Flask
api = Api(app)
global dishID
global mealID
dishID = 0
mealID = 0
dishC = dict()
mealC = dict()

class Key(Resource):
    global dishID
    global dishC
    def get(self,key):
        global dishID
        global dishC
        if key in dishC.keys():
            return make_response(jsonify(dishC[key]), 200)
        else:
            return make_response(jsonify(-5),404)
    def delete (self,key):
        global dishID
        global dishC
        if key in dishC.keys():
            dishC.pop(key)
            return make_response(jsonify(key),200)
        else:
            return make_response(jsonify(-5),404)

class Name(Resource):
    global dishID
    global dishC

    def get(self, key_name):
        for i in range(1, len(dishC) + 1):
            if key_name == dishC[i]["name"]:  # dish is in the collection
                return make_response(jsonify(dishC[i]), 200)
        return make_response(jsonify(-5), 404)

    def delete (self, key_name):
        global dishID
        global dishC
        for i in range(1, len(dishC) + 1):
            if key_name == dishC[i]["name"]:  # dish is in the collection
                dishC.pop(i)
                return make_response(jsonify(i), 200)
        return make_response(jsonify(-5), 404)


class meal_name(Resource):
    global mealC

    def get(self, m_name):
        for i in range(1, len(mealC) + 1):
            if m_name == mealC[i]["name"]:  # meal is in the collection
                return make_response(jsonify(mealC[i]), 200)
        return make_response(jsonify(-5), 404)
    def delete (self, m_name):
        global dishID
        global dishC
        for i in range(1, len(mealC) + 1):
            if m_name == mealC[i]["name"]:  # dish is in the collection
                mealC.pop(i)
                return make_response(jsonify(i), 200)
        return make_response(jsonify(-5), 404)


class meal_id(Resource):
    global mealC

    def get(self, id):
        global mealC
        global mealID
        if id in mealC.keys():
            return make_response(jsonify(mealC[id]), 200)
        else:
            return make_response(jsonify(-5), 404)
    def delete (self,id):
        global dishID
        global dishC
        if id in mealC.keys():
            dishC.pop(id)
            return make_response(jsonify(id),200)
        else:
            return make_response(jsonify(-5),404)

class dishes(Resource):
    global dishC
    def get(self):
        global dishC
        if len(dishC.items()) > 0:
            return make_response(jsonify(dishC),200)

    def delete(self):
        global dishC
        response = -1
        return make_response(jsonify(response), 400)

    def post(self):# to do - what if i sent a json and a query?
        global dishC
        content_type = request.headers.get('Content-Type') #check if it is a application/json if not return 0 and 415 error code
        if content_type != 'application/json':
           return make_response(jsonify(0), 415)
        data = request.get_json()
        if 'name' not in data:#check the attribute name- not correct return -1 and 400
            return make_response(jsonify(-1),400)
        if request.args:
            response = 0
            return make_response(jsonify(response), 415)
        dish_data = request.get_json()
        dish_name = dish_data['name']
        for i in range(1, len(dishC)+1):
            if dish_name ==dishC[i]["name"]:
                make_response(jsonify(-2), 400)
        query = dish_name
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
        response = requests.get(api_url,headers={'X-Api-Key': '5Vocvb2jhJTzHS2WVPNUeg==na0EAyw5FC9Tc7Us'})
        if response.status_code == requests.codes.ok and len(response.json()) > 0:
            info = response.json()[0]
            dish_name = info['name']
            cal = info['calories']
            size = info['serving_size_g']
            sodium = info['sodium_mg']
            suger = info['sugar_g']
            global dishID
            for i in range(1, len(dishC) + 1):
                if dish_name == dishC[i]["name"]:  # dish already exists
                    response = -2
                    return make_response(jsonify(response), 400)

            dishID += 1
            dishC[dishID] = {'name': dish_name, 'ID': dishID, 'cal': cal, 'size': size, 'sodium': sodium,
                             'suger': suger}
            response = dishID
            print(dishC[dishID])
            return make_response(jsonify(response), 201)
        elif response.status_code != requests.codes.ok: #internal problem in server
            response = -4
            return make_response(jsonify(response), 400)
        else:
            response = -3
            return make_response(jsonify(response), 400)

class meals(Resource):
    global mealC
    global mealID

    def delete(self):
        global mealC
        response = -1
        return make_response(jsonify(response), 400)

    def get(self):
        global mealC
        if len(mealC.items()) > 0:
            return make_response(jsonify(mealC), 200)
        else:
            return make_response(jsonify(),400)

    def post (self):
        global mealC
        global mealID
        data = request.get_json()
        if(('name' not in data)  or ('appetizer' not in data) or ('main' not in data) or ('desert' not in data)):
            return make_response(jsonify(-1), 400)
        content_type = request.headers.get('Content-Type')#check if it is a application/json
        if content_type != 'application/json':
            make_response(jsonify(0), 415)
        if request.args:
            response = 0
            return make_response(jsonify(response), 415)
        meal_data = request.get_json()
        meal_name = meal_data['name']
        for i in range(1, len(mealC)+1):
            if meal_name == mealC[i]["name"]:
                return make_response(jsonify(-2), 400)
        mealID += 1
        meal_appetizer_id = (int)(meal_data['appetizer'])
        meal_main_id =(int)(meal_data['main'])
        meal_desert_id = (int)(meal_data['desert'])
        appetizer_found = False
        main_found = False
        desert_found = False
        for i in range (1 ,len(dishC) +1):
            if meal_appetizer_id == dishC[i]["ID"]:
                appetizer_found = True
                break;
        for i in range (1,len(dishC) +1):
            if meal_main_id == dishC[i]["ID"]:
                main_found = True
                break;
        for i in range(1,len(dishC) +1):
            if meal_desert_id == dishC[i]["ID"]:
                desert_found = True
                break;
        if appetizer_found and main_found and desert_found :
            sumCal = (float)(dishC[meal_appetizer_id]["cal"]) +(float)(dishC[meal_main_id]["cal"]) + (float)(dishC[meal_desert_id]["cal"])
            sumSodium =(float)(dishC[meal_appetizer_id]["sodium"]) +(float)(dishC[meal_main_id]["sodium"]) +(float)(dishC[meal_desert_id]["sodium"])
            sumSuger = (float)(dishC[meal_appetizer_id]["suger"]) +(float)(dishC[meal_main_id]["suger"]) +(float)(dishC[meal_desert_id]["suger"])
            mealC[mealID] = {'name':meal_name, 'ID':mealID,'appetizer': meal_appetizer_id, 'main':meal_main_id,'desert':meal_desert_id,'cal':sumCal,'sodium':sumSodium,
                             'suger':sumSuger}
            response = mealID
            print(mealC[mealID])
            return make_response(jsonify(response), 201)
        else:
            response = -5
            return make_response(jsonify(response), 400)
class changes(Resource):
    global mealC
    global mealID
    def put(self,meal_id):
        if meal_id in mealC.keys():
            meal_data = request.get_json()
            need_update = False
            meal_name = (meal_data['name'])
            meal_appetizer_id = (int)(meal_data['appetizer'])
            meal_main_id = (int)(meal_data['main'])
            meal_desert_id = (int)(meal_data['desert'])
            if mealC[mealID]['name'] !=meal_name:
                mealC[mealID]['name'] = meal_name
            if meal_appetizer_id !=mealC[meal_id]['appetizer']:
                mealC[meal_id]['appetizer'] = meal_appetizer_id
                need_update = True
            if meal_main_id != mealC[meal_id]['main']:
                mealC[meal_id]['main'] = meal_main_id
                need_update = True
            if meal_desert_id != mealC[meal_id]['desert']:
                mealC[meal_id]['desert'] = meal_desert_id
                need_update = True
            if need_update == True:
                sumCal = (float)(dishC[meal_appetizer_id]["cal"]) + (float)(dishC[meal_main_id]["cal"]) + (float)(
                    dishC[meal_desert_id]["cal"])
                sumSodium = (float)(dishC[meal_appetizer_id]["sodium"]) + (float)(dishC[meal_main_id]["sodium"]) + (
                    float)(dishC[meal_desert_id]["sodium"])
                sumSuger = (float)(dishC[meal_appetizer_id]["suger"]) + (float)(dishC[meal_main_id]["suger"]) + (float)(
                    dishC[meal_desert_id]["suger"])
                mealC[meal_id]['cal'] = sumCal
                mealC[meal_id]['sodium'] = sumSodium
                mealC[meal_id]['suger'] = sumSuger

            return make_response(jsonify(meal_id), 200)
        else:
            return make_response(jsonify(-5), 400)


api.add_resource(changes, '/meals/<int:meal_id>')
api.add_resource(meal_name, '/meals/<string:m_name>')
api.add_resource(meal_id, '/meals/<int:id>')
api.add_resource(meals, '/meals')
api.add_resource(dishes, '/dishes')
api.add_resource(Key, '/dishes/<int:key>')
api.add_resource(Name, '/dishes/<string:key_name>')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

from flask import Flask, render_template, request, url_for, jsonify
from MultiSegementEvolution import evolution 
from MixedIntiativeEvolution import mi_evolution
import json 
from MonsterManual import MONSTER_MANUAL , PLAYER_MANUAL
import requests
from flask_cors import CORS, cross_origin
app = Flask(__name__)
#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/result')
def result():
   dict = {'phy':50,'che':60,'maths':70}
   return render_template('result.html', result = dict)


@app.route('/send')
def send_request():
   party =  ["Dwarf cleric" , "Elf wizard 2",  "Halfing rogue",  "Human fighter",  "Human figher 2"] 
   monsters = list(MONSTER_MANUAL.keys())[:4]
   ideal_difficulty = [1]

   req = {"party": party, "monsters": monsters, "difficulty": ideal_difficulty}
   j = json.dumps(req)
   
   server_return = requests.post('http://localhost:5000/evolve', json=req)
   print(server_return)
   return server_return.text

@app.route('/evolve', methods=['POST'])
@cross_origin()
def evolve():
   request_data = request.get_json() 


   party = None 
   monsters = None 
   ideal_difficulty = None 

   generations = 5 
   popsize = 30 
   elitism = 3 

   if "party" in request_data:
      party = request_data["party"]
   
   if "monsters" in request_data:
      monsters = request_data["monsters"]
   
   if "difficulty" in request_data:
      ideal_difficulty =  [float(diff) for diff in request_data["difficulty"]] 
   
   if "generations" in request_data:
      generations = int(request_data["generations"])
   
   if "popsize" in request_data:
      popsize  = int(request_data["popsize"])
   
   if "elitism" in request_data:
      elitism = int(request_data["elitism"])
   #party =  ["Dwarf cleric" , "Elf wizard 2",  "Halfing rogue",  "Human fighter",  "Human figher 2"] 
   #monsters = list(MONSTER_MANUAL.keys())
   #ideal_difficulty = 1
   print(party, monsters, ideal_difficulty)
   if not party is None and not monsters is None and not ideal_difficulty is None:
      encounter, history = evolution(party, monsters, ideal_difficulty, generations, popsize,elitism , 0.5, 1)
      #print(encounter)
      response = jsonify({"fitness": encounter[0], "stages": encounter[1].stages})
      return response
   else:
      response = jsonify(message = "invalid input")
      return response
   

@app.route('/mi-evolve', methods=['POST'])
@cross_origin()
def mi_evolve():
   request_data = request.get_json() 


   party = None 
   stage_settings= None 

   generations = 5 
   popsize = 30 
   elitism = 3 

   if "party" in request_data:
      party = request_data["party"]
   
   if "stageSettings" in request_data:
      stage_settings = request_data["stageSettings"]
   
   
   if "generations" in request_data:
      generations = int(request_data["generations"])
   
   if "popsize" in request_data:
      popsize  = int(request_data["popsize"])
   
   if "elitism" in request_data:
      elitism = int(request_data["elitism"])

   if not party is None and not stage_settings is None:
      encounter, history = mi_evolution(party, stage_settings, generations, popsize,elitism , 0.5, 1)
      #print(encounter)
      response = jsonify({"fitness": encounter[0], "stages": encounter[1].stages})
      return response
   else:
      response = jsonify(message = "invalid input")
      return response

@app.route('/monsters', methods=['GET'])
@cross_origin()
def get_monsters():
   monsters = list(MONSTER_MANUAL.keys())
   response = jsonify(monsters)
   return response

@app.route('/players', methods=['GET'])
@cross_origin()
def get_players():
   monsters = list(PLAYER_MANUAL.keys())
   response = jsonify(monsters)
   return response

if __name__ == '__main__':
   app.run(debug = True)
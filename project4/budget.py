from flask import Flask, request, render_template
from werkzeug.exceptions import abort
import json

app = Flask(__name__)

uncat_pur=[0,]


#CATS = {
#	"cat1": {"name": "house", "limit": 100, "remaining": 100},
#	"cat2": {"name": "food", "limit": 100, "remaining": -10}
#}
CATS={}
#dictionary for purchases
#PURS ={
#	"pur1":{"amount": 0, "date": "04-04-2020", "category": "house"}
#}
PURS={}
#uncategorized purchases amount


def abort_if_cat_doesnt_exist(cat_id):
	if cat_id not in CATS:
		abort(404)

def abort_if_pur_doesnt_exist(pur_id):
	if pur_id not in PURS:
		abort(404)

@app.route("/")
def set_app():
	#TEST
	#print(type(PURS)) ---- this is a dict
	return render_template("app.html", cat_list=CATS, pur_list=PURS)


# RESTful access to the list of todos
@app.route("/cats", methods=["GET"])
def list_get():
	# Flask automatically jsonify's dictionaries
	return CATS

@app.route("/cats", methods=["POST"])
def list_post():
	# Get json request data
	req_data = request.get_json()

	# Calculate next available id value
	cat_id=-1
	if not CATS:
		cat_id = "cat1"
	else:
		cat_id = int(max(CATS.keys()).lstrip("cat")) + 1
		cat_id = f"cat{cat_id}"

	# Add todo item
	CATS[cat_id] = {"name": req_data["name"], "limit": req_data["limit"], "remaining": req_data["limit"]}

	# If returning a tuple, second arg can be a response code
	return {cat_id: CATS[cat_id]}, 201

@app.route("/uncat", methods=["GET"])
def uncat_get():
	# Flask automatically jsonify's dictionaries
	return json.dumps(uncat_pur)

# RESTful access to individual todo resources
@app.route("/cats/<cat_id>", methods=["GET"])
def single_get(cat_id=None):
	# Check that the requested resource actually exists
	abort_if_cat_doesnt_exist(cat_id)

	return CATS[cat_id]

@app.route("/cats/<cat_id>", methods=["DELETE"])
def single_delete(cat_id=None):
	abort_if_cat_doesnt_exist(cat_id)

	del CATS[cat_id]

	return "", 204


# RESTful access to the list of purchases
@app.route("/purchases", methods=["GET"])
def purs_get():
	# Flask automatically jsonify's dictionaries
	return PURS

@app.route("/purchases", methods=["POST"])
def purs_post():
	# Get json request data
	req_data = request.get_json()

	# Calculate next available id value
	if not PURS:
		pur_id=1
	else:
		pur_id = int(max(PURS.keys()).lstrip("pur")) + 1
	

	# Add item
	#PURS[pur_id] = {"amount": req_data["amount"], "date": req_data["date"], "category": req_data["category"]}

	if "category" in req_data and (req_data["category"]!=""):
		pur_id = f"pur{pur_id}"
		PURS[pur_id] = {"amount": req_data["amount"], "date": req_data["date"], "category": req_data["category"]}
		# find the category
		for cat_id in CATS:
			if CATS[cat_id]["name"].lower()==req_data["category"].lower():
				CATS[cat_id]["remaining"] = CATS[cat_id]["remaining"]-req_data["amount"]
		return {pur_id: PURS[pur_id]}, 201
	else:
		#PURS[pur_id] = {"amount": req_data["amount"], "date": req_data["date"]}
		uncat_pur[0] = uncat_pur[0]+req_data["amount"]
		pur_id = f"pur{pur_id-1}"
		return {}, 201
	# If returning a tuple, second arg can be a response code
	



# RESTful access to individual todo resources
@app.route("/purchases/<pur_id>", methods=["GET"])
def purs_single_get(pur_id=None):
	# Check that the requested resource actually exists
	abort_if_pur_doesnt_exist(pur_id)

	return PURS[pur_id]




if __name__ == "__main__":
	app.run(debug=True)

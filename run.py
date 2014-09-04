from flask import Flask, request, json
import redis
import requests

app = Flask(__name__)

r = redis.from_url("redis://redistogo:273b30ab7575c845853f491ac4797121@grouper.redistogo.com:10434")

@app.route("/", methods = ['GET', 'POST'])
def hello():
	text = request.args["text"]
	user_name = request.args["user_name"]
	if (text == None):
		return None
	migrationNumber = 0
	parts = text.split(" ")
	currentMigration = {"username": "no one", "number": 0}
	currentMigrationString = r.get("slack:taking")
	if isinstance(currentMigrationString, str):
		try:
			currentMigration = json.loads(currentMigrationString)
		except:
			r.set(json.dumps(currentMigration))
			return "Uh oh. Something went wrong with trying to get the current migration from redis."
	if (text == "current"): return "Current migration number is " + str(currentMigration["number"]) + " taken by " + currentMigration["username"]
	if text == "next":
	    next = currentMigration["number"] + 1
	    currentMigration = {"username": user_name, "number": next}
	    r.set("slack:taking", json.dumps(currentMigration))
	    PinBotMessage(user_name + " is taking migration #" + str(currentMigration["number"]))
	    return ""
	elif parts[0] == "set":
		try:
			migrationNumber = int(parts[1])
		except:
			print parts[1]
			return "The /taking set command requires you enter an integer afterwards"
		currentMigration["number"] = migrationNumber
		currentMigration["username"] = user_name
		r.set("slack:taking", json.dumps(currentMigration))
		PinBotMessage(user_name + " has set the migration number to " + str(currentMigration["number"]))
	else:
		return "/taking is the database migration system for Careers on Slack. You can get the current migration number user /taking current. To reserve a migration, type '/taking next'. To set the migration number type '/taking set [number]'."
	return ""

def PinBotMessage(message):
	requests.post("https://stackexchange.slack.com/services/hooks/incoming-webhook?token=gjsygaVMvs9dRMRL7I7dSF7H", json.dumps({"text": message}))

if __name__ == "__main__":
	app.debug = True
	app.run()
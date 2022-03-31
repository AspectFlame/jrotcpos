from flask import Flask, request
from flask import render_template
from flask import request
from flask import jsonify
import json
import psycopg2

#Flask application instance

conn = psycopg2.connect(
   database="pointofsale", user='postgres', password='toor', host='127.0.0.1', port='5432'
)
cursor = conn.cursor()

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route('/get_items', methods=["POST", "GET"])
def get_items():
    # data = request.get_json(force=True)
    cursor.execute('SELECT * FROM product_items')
    data = cursor.fetchall()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    #return json.dumps(error_data)

@app.route('/get_categories', methods=["POST", "GET"])
def get_categories():
    cursor.execute('SELECT * from product_category')
    data = cursor.fetchall()
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(port=5001)
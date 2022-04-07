from flask import Flask, request
from flask import render_template
from flask import request
from flask import jsonify
import json
import psycopg2
from flask_cors import CORS

#Flask application instance

conn = psycopg2.connect(
   database="pointofsale", user='postgres', password='pointofsale', host='127.0.0.1', port='5432'
)
cursor = conn.cursor()

app = Flask(__name__)

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
app.after_request(add_cors_headers)


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route('/get_items', methods=["POST", "GET"])
def get_items():
    category_id = request.form.get('category_id')
    cursor.execute('SELECT * FROM product_items INNER JOIN product_category ON product_category.id=%s', (category_id))
    data = cursor.fetchall()
    response = jsonify(data)
    return response
    #return json.dumps(error_data)

@app.route('/get_users', methods=["POST", "GET"])
def get_users():
    # users = request.form.get('users_id')
    cursor.execute('SELECT * FROM users WHERE expiration_date IS null')
    data = cursor.fetchall()
    response = jsonify(data)
    return response

@app.route('/get_categories', methods=["POST", "GET"])
def get_categories():
    cursor.execute('SELECT * from product_category')
    data = cursor.fetchall()
    response = jsonify(data)
    return response


if __name__ == '__main__':
    app.run(port=5001)
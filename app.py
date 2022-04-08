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
    category_id = str(request.form.get('category_id'))
    cursor.execute('SELECT * FROM product_items INNER JOIN product_category ON product_category.id=%s', (category_id,))
    data = cursor.fetchall()
    response = jsonify(data)
    return response
    #return json.dumps(error_data)

@app.route('/get_users', methods=["POST", "GET"])
def get_users():
    cursor.execute('SELECT * FROM users WHERE expiration_date IS null')
    data = cursor.fetchall()
    response = jsonify(data)
    return response

def get_users_by_email(email):
    cursor.execute('SELECT * FROM users WHERE expiration_date is null and email=%s', (email,))
    userrec = cursor.fetchall()
    return userrec

@app.route('/get_categories', methods=["POST", "GET"])
def get_categories():
    cursor.execute('SELECT * from product_category')
    data = cursor.fetchall()
    response = jsonify(data)
    return response

@app.route('/create_order', methods=["PUT"])
def create_order():
    recipientCards = request.form.get('recipient_cards')
    recipientCardJSON = json.loads(recipientCards)
    print(recipientCardJSON[0])
    customerEmail = str(request.form.get('customer_email'))
    customer = get_users_by_email(customerEmail)
    cursor.execute('insert into orders (customer_users_fk, date_ordered) values (%s, current_timestamp)', (customer[0][0],))
    cursor.execute('select MAX(id) AS orderid FROM orders')
    data = cursor.fetchall()
    orderid = data[0][0]
    print(orderid)
    for card in recipientCardJSON: 
        print(card['recipientEmail'])
        recipient = get_users_by_email(card['recipientEmail'])
        cursor.execute('insert into order_recipients (order_id_fk, recipient_users_fk, gift_msg) values (%s, %s, %s)', (orderid, recipient[0][0], card['message'])) 
    response = jsonify(orderid)
    return response


if __name__ == '__main__':
    app.run(port=5001)
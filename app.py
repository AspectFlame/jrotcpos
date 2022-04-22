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
conn.autocommit = True
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
    customerEmail = str(request.form.get('customer_email'))
    customer = get_users_by_email(customerEmail)
    cursor.execute('insert into orders (customer_users_fk, date_ordered) values (%s, current_timestamp)', (customer[0][0],))
    cursor.execute('select MAX(id) AS orderid FROM orders')
    data = cursor.fetchall()
    orderid = data[0][0]
    if orderid == 0:
        return jsonify({'success': False, error: 'Order ID not found'})
    print(orderid)
    for card in recipientCardJSON: 
        print(card['recipientEmail'])
        recipient = get_users_by_email(card['recipientEmail'])
        cursor.execute('insert into order_recipients (order_id_fk, recipient_users_fk, gift_msg) values (%s, %s, %s)', (orderid, recipient[0][0], card['message'])) 
        cursor.execute('select MAX(id) AS order_recipient_id FROM order_recipients WHERE order_id_fk = %s', (orderid,))
        data = cursor.fetchall()
        order_recipient_id = data[0][0]
        if (order_recipient_id == 0):
            return jsonify({'success': False, error: 'Order recipient ID not found'})
        cardValues = card['values']
        print(cardValues)
        for key in cardValues:
            print(key, cardValues[key])
            cursor.execute('insert into order_recipient_items (order_recipient_fk, product_items_fk, quantity) values (%s, %s, %s)', (order_recipient_id, key, cardValues[key]))

    response = jsonify({'success': True})
    return response



@app.route('/get_order_info', methods=["POST", "GET"])
def get_order_info():
    confirmed = request.form.get('confirmed')
    print(confirmed)
    cursor.execute('select o.id order_id, u.email customer_email, or_rec.gift_msg recipient_gift_msg, rec.first_name recipient_fn, rec.last_name recipient_ln, rec.email recipient_email, rec.block_1_room_num block_1, rec.block_2_room_num block_2, rec.block_3_room_num block_3, rec.block_4_room_num block_4, rec.block_5_room_num block_5, rec.block_6_room_num block_6, rec.block_7_room_num block_7, rec.advisory_room_num adv, pi.name product_name, ori.quantity order_quantity, or_rec.id or_rec_id, ori.id ori_id, pi.id product_id from orders o, users u, users rec, order_recipients or_rec, order_recipient_items ori, product_items pi where o.customer_users_fk = u.id and or_rec.order_id_fk = o.id and or_rec.recipient_users_fk = rec.id and ori.order_recipient_fk = or_rec.id and ori.product_items_fk = pi.id and or_rec.confirmed = %s', (confirmed,))
    data = cursor.fetchall()
    response = jsonify(data)
    return response



@app.route('/delete_order', methods=["DELETE"])
def delete_order():
    orderid = request.form.get('order_id')
    cursor.execute('select * from order_recipients where order_id_fk = %s', (orderid,))
    data = cursor.fetchall()
    for orderrecipient in data:
        cursor.execute('DELETE from order_recipient_items where order_recipient_fk = %s', (orderrecipient[0],))
    cursor.execute('DELETE from order_recipients WHERE order_id_fk = %s', (orderid,))
    cursor.execute('DELETE from orders where id = %s', (orderid,))
    response = jsonify({'success': True})
    return response

@app.route('/confirm_order', methods=["POST"])
def confirm_order():
    orderid = request.form.get('order_id')
    print(orderid)
    cursor.execute('UPDATE order_recipients SET confirmed=true WHERE order_id_fk = %s', (orderid,))
    cursor.execute('select * from order_recipients where order_id_fk = %s', (orderid,))
    data = cursor.fetchall()
    response = jsonify(data)
    return response
    
if __name__ == '__main__':
    app.run(port=5001)
    
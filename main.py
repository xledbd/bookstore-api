# app.py
from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import json
from metrics import setup_metrics
from logger import setup_logging, log_request_middleware

app = Flask(__name__)
setup_metrics(app)
setup_logging()
log_request_middleware(app)
CORS(app)

# Configure DynamoDB connection
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
books_table = dynamodb.Table("Books")

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# Mock categories - Consider moving to DynamoDB as well
mock_categories = [
    {"id": "classics", "name": "Classics", "description": "Timeless masterpieces from renowned authors."},
    {"id": "modern", "name": "Modern Literature", "description": "Contemporary works from modern authors."},
    {"id": "poetry", "name": "Poetry", "description": "Beautiful poetry from literary giants."},
    {"id": "fiction", "name": "Fiction", "description": "Fictional works with universal appeal."},
    {"id": "fantasy", "name": "Fantasy", "description": "Magical and fantastical stories."},
    {"id": "science", "name": "Science", "description": "Scientific exploration and discovery."}
]

# Mock cart data
mock_cart = []

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(mock_categories)

@app.route('/api/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    category = next((c for c in mock_categories if c['id'] == category_id), None)
    if category:
        return jsonify(category)
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/categories/<category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    # Query DynamoDB for products in this category
    response = books_table.scan(
        FilterExpression=Attr('categoryId').eq(category_id)
    )
    items = response['Items']

    # Handle pagination if there are more items
    while 'LastEvaluatedKey' in response:
        response = books_table.scan(
            FilterExpression=Attr('categoryId').eq(category_id),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])

    return json.dumps(items, cls=DecimalEncoder)

@app.route('/api/products/featured', methods=['GET'])
def get_featured_products():
    # Return a subset of products as featured
    featured_ids = ["1", "3", "7", "11","8"]
    featured_products = []

    # Get each featured product by ID
    for product_id in featured_ids:
        response = books_table.get_item(
            Key={"id": product_id}
        )
        if 'Item' in response:
            featured_products.append(response['Item'])

    return json.dumps(featured_products, cls=DecimalEncoder)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    response = books_table.get_item(
        Key={'id': product_id}
    )
    
    if 'Item' in response:
        return json.dumps(response['Item'], cls=DecimalEncoder)
    
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart():
    return jsonify(mock_cart)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)

    # Get product from DynamoDB
    response = books_table.get_item(
        Key={'id': product_id}
    )

    if 'Item' not in response:
        return jsonify({"error": "Product not found"}), 404
    
    product = response['Item']
    
    # Check if the product is already in the cart
    cart_item = next((item for item in mock_cart if item['id'] == product_id), None)
    if cart_item:
        cart_item['quantity'] += quantity
    else:
        # Convert Decimal to float for price
        product_price = float(product['price']) if isinstance(product['price'], Decimal) else product['price']

        mock_cart.append({
            "id": product_id,
            "name": product['name'],
            "author": product['author'],
            "price": product_price,
            "quantity": quantity,
            "imageUrl": product['imageUrl']
        })
    
    return jsonify({"success": True})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    item_id = data.get('itemId')
    quantity = data.get('quantity')
    
    item = next((item for item in mock_cart if item['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found in cart"}), 404
    
    item['quantity'] = quantity
    return jsonify({"success": True})

@app.route('/api/cart/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    global mock_cart
    mock_cart = [item for item in mock_cart if item['id'] != item_id]
    return jsonify({"success": True})

@app.route('/api/cart/checkout', methods=['POST'])
def checkout():
    global mock_cart
    # In a real app, we would process payment, create order, etc.
    mock_cart = []
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
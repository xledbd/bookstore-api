import boto3
import json
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Books")

# Load books from JSON file
with open("books.json", "r") as f:
    books_json = json.load(f)

# Convert float values to Decimal
def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    else:
        return obj
    
# Convert all books
books = convert_floats_to_decimal(books_json)

# Insert each book into DynamoDB
for book in books:
    response = table.put_item(Item=book)
    print(f"Added book: {book['name']} with ID: {book['id']}")

print("All books have been added to DynamoDB")

from flask import Flask, request, jsonify
from constants import Constants
import pymongo
from functools import wraps
import jwt
import datetime
from flask_bcrypt import Bcrypt
import secrets
import uuid

app = Flask(__name__)

# Create a connection to your MongoDB Atlas cluster
client = pymongo.MongoClient(Constants.MONGODB_URL)

# Access the database and collections
db = client.get_database(Constants.MONGODB_DB)
users_collection = db.users
templates_collection = db.templates

bcrypt = Bcrypt(app)
SECRET_KEY = secrets.token_hex(32)
app.config['SECRET_KEY'] = SECRET_KEY


# Decorator for JWT token verification
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Invalid token!'}), 403
        
        token = token.split(' ')[1]

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users_collection.find_one({'email': data['email']})
        except jwt.ExpiredSignatureError as e:
            print(f"Expired token: {e}")
            return jsonify({'message': 'Token has expired'}), 403
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return jsonify({'message': 'Invalid token'}), 403
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 403

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    
    # Check if a user with the same email already exists
    existing_user = users_collection.find_one({'email': email})
    
    if existing_user:
        return jsonify({'message': 'Email is already in use'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    # Save user data to MongoDB
    users_collection.insert_one({
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'email': data['email'],
        'password': hashed_password
    })

    return jsonify({'message': 'User registered'})


@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    # Fetch user from MongoDB using auth['email']
    user = users_collection.find_one({'email': auth['email']})

    if user and bcrypt.check_password_hash(user['password'], auth['password']):
        token = jwt.encode({
            'email': auth['email'], 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'access_token': token})
    
    return jsonify({'message': 'Login failed'})


@app.route('/template', methods=['POST'])
@token_required
def create_template(current_user):
    data = request.get_json()
    # Generate a UUID for the new template
    template_id = str(uuid.uuid4())
    # Save the template data to MongoDB
    new_template = {
        '_id': template_id,
        'template_name': data['template_name'],
        'subject': data['subject'],
        'body': data['body'],
        'created_by': current_user['email']
    }
    templates_collection.insert_one(new_template)

    return jsonify({'message': 'Template created', 'template': new_template})


@app.route('/template', methods=['GET'])
@token_required
def get_all_templates(current_user):
    # Retrieve and return all templates from MongoDB
    templates = templates_collection.find({'created_by': current_user['email']})
    template_list = []
    for template in templates:
        template_list.append({
            '_id': template['_id'],
            'template_name': template['template_name'],
            'subject': template['subject'],
            'body': template['body'],
            'created_by': template['created_by']
        })

    return jsonify({'templates': template_list})


@app.route('/template/<template_id>', methods=['GET'])
@token_required
def get_template(current_user, template_id):
    # Retrieve and return a single template by template_id from MongoDB
    template = templates_collection.find_one({'_id': template_id, 'created_by': current_user['email']})
    
    if template:
        return jsonify({
            '_id': template['_id'],
            'template_name': template['template_name'],
            'subject': template['subject'],
            'body': template['body'],
            'created_by': template['created_by']
        })
    
    return jsonify({'message': 'Template not found'})


@app.route('/template/<template_id>', methods=['PUT'])
@token_required
def update_template(current_user, template_id):
    data = request.get_json()
    template = templates_collection.find_one({'_id': template_id})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    if template['created_by'] != current_user['email']:
        return jsonify({'message': 'Unauthorized access'}), 403
    
    # Update the template in MongoDB with the new data
    templates_collection.update_one({'_id': template_id}, {'$set': {
        'template_name': data['template_name'],
        'subject': data['subject'],
        'body': data['body']
    }})

    updated_template = templates_collection.find_one({'_id': template_id})

    return jsonify({'message': 'Template updated', 'template': updated_template})


@app.route('/template/<template_id>', methods=['DELETE'])
@token_required
def delete_template(current_user, template_id):
    template = templates_collection.find_one({'_id': template_id})

    if not template:
        return jsonify({'message': 'Template not found'}), 404

    if template['created_by'] != current_user['email']:
        return jsonify({'message': 'Unauthorized access'}), 403
    
    # Delete the template with the given template_id from MongoDB
    templates_collection.delete_one({'_id': template_id})
    
    return jsonify({'message': 'Template deleted'})


if __name__ == '__main__':
    app.run(debug=True)

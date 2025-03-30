from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([{
        "id": m.id,
        "body": m.body,
        "username": m.username,
        "created_at": m.created_at,
        "updated_at": m.updated_at
    } for m in messages])

# GET a single message by ID
@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = Message.query.get(id)
    if message:
        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at,
            "updated_at": message.updated_at
        })
    return jsonify({"error": "Message not found"}), 404

# POST a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or "body" not in data or "username" not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    new_message = Message(
        body=data["body"],
        username=data["username"]
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "id": new_message.id,
        "body": new_message.body,
        "username": new_message.username,
        "created_at": new_message.created_at,
        "updated_at": new_message.updated_at
    }), 201

# PATCH (update) an existing message
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    data = request.get_json()
    if "body" in data:
        message.body = data["body"]
        message.updated_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({
        "id": message.id,
        "body": message.body,
        "username": message.username,
        "created_at": message.created_at,
        "updated_at": message.updated_at
    })

# DELETE a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({"message": "Message deleted"}), 200

if __name__ == '__main__':
    app.run(port=5555)

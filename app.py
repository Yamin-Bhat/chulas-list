from flask import Flask, request, jsonify , render_template , redirect , url_for , session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv() 
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chulas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)

ADMIN_USERNAME = 'YAMIN'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

class Chula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    head = db.Column(db.String(100), nullable=True)
    members = db.Column(db.Text, nullable=False)

# Create DB
with app.app_context():
    db.create_all()




# Test route
@app.route('/api/ping')
def ping():
    return jsonify({"message": "API is working!"})



@app.route('/api/chulas', methods=['GET'])
def get_all_chulas():
    chulas = Chula.query.all()  # Get all rows from the database

    result = []
    for chula in chulas:
        result.append({
            "id": chula.id,
            "name": chula.name,
            "head": chula.head,
            "members": [m.strip() for m in chula.members.split(',')]
        })

    return jsonify(result), 200

@app.route('/api/chulas', methods=['POST'])
def add_chula():
    data = request.get_json()

    # Basic validation
    if not data or 'name' not in data or 'members' not in data:
        return jsonify({"error": "Missing required fields: name and members"}), 400

    new_chula = Chula(
        name=data['name'],
        head=data.get('head'),  # Optional
        members=data['members']
    )

    db.session.add(new_chula)
    db.session.commit()

    return jsonify({"message": "Chula added successfully", "id": new_chula.id}), 201

@app.route('/api/chulas/<int:chula_id>', methods=['GET'])
def get_chula(chula_id):
    chula = Chula.query.get(chula_id)

    if not chula:
        return jsonify("Chula not found"), 404

    result = {
        "id": chula.id,
        "name": chula.name,
        "head": chula.head,
        "members": [m.strip() for m in chula.members.split(',')]
    }

    return jsonify(result), 200

@app.route('/api/chulas/<int:chula_id>', methods=['PUT'])
def update_chula(chula_id):
    chula = Chula.query.get(chula_id)

    if not chula:
        return jsonify({"error": "Chula not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    chula.name = data.get('name', chula.name)
    chula.head = data.get('head', chula.head)
    chula.members = data.get('members', chula.members)

    db.session.commit()

    return jsonify({"message": "Chula updated successfully"}), 200

@app.route('/')
def index():
    return render_template('index.html' , is_admin=session.get('logged_in', False))



if __name__ == '__main__':
    app.run(debug=True , port = 5001)
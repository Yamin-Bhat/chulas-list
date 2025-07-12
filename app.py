from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # change this in production

# Set up the SQLite database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chulas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ----------------------
# Database Model
# ----------------------
class Chula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    head = db.Column(db.String(100))  # ✅ New field: Chula head
    members = db.Column(db.Text, nullable=False)

# ----------------------
# Home with Search
# ----------------------
@app.route('/', methods=['GET'])
def home():
    search_query = request.args.get('q', '')
    if search_query:
        chulas = Chula.query.filter(Chula.name.ilike(f"%{search_query}%")).all()
    else:
        chulas = Chula.query.all()
    return render_template("index.html", chulas=chulas, search_query=search_query)

# ----------------------
# View Chula Details
# ----------------------
@app.route('/chula/<int:chula_id>')
def view_chula(chula_id):
    chula = Chula.query.get_or_404(chula_id)
    return render_template("chula_detail.html", chula=chula)

# ----------------------
# Admin Login
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "password":
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            return "Invalid login"

    return render_template("login.html")

# ----------------------
# Admin Logout
# ----------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# ----------------------
# Admin Page: Add New Chula
# ----------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return "Access denied", 403

    if request.method == 'POST':
        name = request.form['name']
        head = request.form['head']
        members = request.form['members']
        new_chula = Chula(name=name, head=head, members=members)
        db.session.add(new_chula)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("admin.html")

# ----------------------
# Edit Chula
# ----------------------
@app.route('/edit/<int:chula_id>', methods=['GET', 'POST'])
def edit_chula(chula_id):
    if 'admin' not in session:
        return "Access denied", 403

    chula = Chula.query.get_or_404(chula_id)

    if request.method == 'POST':
        chula.name = request.form['name']
        chula.head = request.form['head']
        chula.members = request.form['members']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit_chula.html", chula=chula)

# ----------------------
# Run the app
# ----------------------
if __name__ == '__main__':
    # Create instance folder and DB if needed
    if not os.path.exists('instance'):
        os.makedirs('instance')
    with app.app_context():
        db.create_all()
    app.run(debug=True)

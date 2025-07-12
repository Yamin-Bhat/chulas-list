from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'yamin_secret_key'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chulas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Admin login details
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "pass123"

# Chula model
class Chula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    members = db.Column(db.String(500), nullable=False)  # stored as comma-separated names

# Create DB tables if not exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    chulas = Chula.query.all()
    return render_template("index.html", chulas=chulas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "Invalid login!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        chula_name = request.form['chula_name']
        members = request.form['members']
        new_chula = Chula(name=chula_name, members=members)
        db.session.add(new_chula)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('admin.html')
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


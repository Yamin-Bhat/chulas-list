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

@app.route('/', methods=['GET'])
def home():
    search_query = request.args.get('q', '')
    if search_query:
        chulas = Chula.query.filter(Chula.name.ilike(f"%{search_query}%")).all()
    else:
        chulas = Chula.query.all()
    return render_template("index.html", chulas=chulas, search_query=search_query)


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

@app.route('/chula/<int:chula_id>')
def view_chula(chula_id):
    chula = Chula.query.get_or_404(chula_id)
    return render_template("chula_detail.html", chula=chula)

@app.route('/edit/<int:chula_id>', methods=['GET', 'POST'])
def edit_chula(chula_id):
    if 'admin' not in session:
        return "Access denied", 403

    chula = Chula.query.get_or_404(chula_id)

    if request.method == 'POST':
        chula.name = request.form['name']
        chula.members = request.form['members']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit_chula.html", chula=chula)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


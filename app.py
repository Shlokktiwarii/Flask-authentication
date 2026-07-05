from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,login_user, login_required , current_user
from sqlalchemy import text
import re
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f'<User {self.username}>'
    


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Shlok_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    
    @app.route("/health/db")
    def health_db():
       try:
           db.session.execute(text("SELECT 1"))
           return{"db":"healthy"},200
       except Exception as e:
           return {"db":"error","detail": str(e)},500
       

    with app.app_context():
        db.create_all()


   
   
    @app.route('/')
    def index():
        return render_template('index.html')
    

    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    


    @app.route('/register', methods = ["GET", "POST"])
    def register():

        errors = []  

        if request.method == "POST":
            username = (request.form.get('username') or "").strip()
            email = (request.form.get('email') or "").strip()
            password = request.form.get('password') or ""
            confirm = request.form.get('confirm_password') or ""

            if not (3 <= len(username) <= 50):
                errors.append("Username must be between 3 and 50 characters.")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Invalid email address.")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            if password != confirm:
                errors.append("Password don't match.")
            # print("Form submitted",username ,email ,password ,confirm )
            if not errors:
                pw_hash = generate_password_hash(password)
                new_user = User(username=username, email=email, password_hash=pw_hash)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect(url_for('login'))
                except IntegrityError:
                    db.session.rollback()   
                    errors.append("Username or email already exists.")


        return render_template('register.html',errors = errors)

    @app.route('/login',methods = ["GET", "POST"])
    def login():

        errors = []
        if request.method == "POST":
            email = (request.form.get('email') or "").strip()
            password = request.form.get('password') or ""

            if not email:
                errors.append("Email is required.")
            if not password:
                errors.append("Password is required.")
            if not errors:
                user = User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password_hash, password):
                errors.append("Invalid email or password.")
            else:
                login_user(user)
                return redirect(url_for('dashboard'))
            

        return render_template('login.html',errors = errors)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


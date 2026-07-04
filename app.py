from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy import text

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

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @login_manager.user_loader
    def load_user(user_id):
        return None

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


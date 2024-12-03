from flask import Flask, render_template, request, redirect, session, flash, url_for
from auth import UserSession
from notifications import NotificationManager
from password_generator import PasswordBuilder
from ui_manager import UIManager
from data_proxy import SensitiveDataProxy
from recovery import RecoveryHandler
from models import VaultDetail, db, User, VaultItem
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = "secretkey"  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mypass.db'  # Using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warnings
db.init_app(app)


# Initialize Singletons
user_session = UserSession()
notification_manager = NotificationManager()
ui_manager = UIManager()

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Database initialized.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')  # Return the register template again

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))

        # Create a new user
        user = User(email=email)
        user.set_password(password)  # Assuming you have a set_password method
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))  # Redirect to login after successful registration

    # Render the registration template for GET requests
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and verify the password
        if user and check_password_hash(user.password_hash, password):
            # Store user information in the session
            session['user_id'] = user.id
            session['email'] = user.email  # Store additional user info if needed
            
            flash("Login successful!", "success")
            return redirect(url_for('vault'))  # Redirect to the user's vault or home page
            
        else:
            flash("Invalid email or password.", "danger")
            return render_template('login.html')  # Render login template again on failure

     # Render the login template for GET requests
     return render_template('login.html')

@app.route('/vault', methods=['GET', 'POST'])
def vault():
    if 'user_id' not in session:
        flash("Please log in to access your vault.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Fetch user's vault items and their details
    vault_items = VaultItem.query.filter_by(user_id=user_id).all()

    # Handle adding a new vault item if POST request
    if request.method == 'POST':
        if 'add_item' in request.form:
            item_type = request.form['item_type']  # e.g., 'login', 'credit_card', 'secure_note'
            title = request.form['title']           # Title of the vault item
            new_item = VaultItem(user_id=user_id, item_type=item_type, title=title)
            db.session.add(new_item)
            db.session.commit()

            # Add details for the new vault item
            for key in request.form.getlist('detail_key'):
                value = request.form.getlist('detail_value')[key]
                new_detail = VaultDetail(vault_item_id=new_item.id, key=key, value=value)
                db.session.add(new_detail)
            db.session.commit()

            flash("Vault item added successfully!", "success")
            return redirect(url_for('vault'))

    # Render vault items with details
    return ui_manager.render_vault(vault_items)
    

@app.route('/generate_password', methods=['GET', 'POST'])
def generate_password():
    if request.method == 'POST':
        length = int(request.form.get('length'))
        complexity = request.form.get('complexity')
        password = PasswordBuilder().set_length(length).set_complexity(complexity).build()
        return render_template('password.html', password=password)
    return render_template('password_generator.html')

@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    if request.method == 'POST':
        email = request.form['email']
        answers = [
            request.form['answer1'],
            request.form['answer2'],
            request.form['answer3']
        ]

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('recovery'))

        # Attempt to recover the password using the chain of responsibility
        if recovery.recover(user, answers):
            flash("Password recovery successful! You may now reset your password.", "success")
            # Here you could redirect to a reset password page
            return redirect(url_for('reset_password', user_id=user.id))
        else:
            flash("One or more answers were incorrect. Please try again.", "danger")
            return redirect(url_for('recovery'))

    return render_template('recovery.html')
    

if __name__ == '__main__':
    app.run(debug=True)

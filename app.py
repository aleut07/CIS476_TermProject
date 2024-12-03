from os import name
from flask import Flask, render_template, request, redirect, session, flash, url_for
from auth import UserSession
from notifications import NotificationManager
from password_generator import PasswordBuilder
from ui_manager import UIManager
from recovery import RecoveryHandler, SecurityQuestionHandler
from data_proxy import SensitiveDataProxy
from recovery import RecoveryHandler
from models import SecurityQuestion, VaultDetail, db, User, VaultItem
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate)
app.secret_key = "secretkey"  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CIS476_TermProject.db'  # Using SQLite
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
    predefined_questions = [
        "What was the name of your first pet?",
        "What is your mother's maiden name?",
        "What city were you born in?",
        "What is your favorite color?",
        "What high school did you attend?"
    ]

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        answers = [
            request.form.get('security_answer_1'),
            request.form.get('security_answer_2'),
            request.form.get('security_answer_3')
        ]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', security_questions=predefined_questions)

        if not all(answers):
            flash("All security answers are required.", "danger")
            return render_template('register.html', security_questions=predefined_questions)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))

        # Create and save the user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()  # Commit user first to get the user.id

        # Add security questions and answers
        for question, answer in zip(predefined_questions[:3], answers):
            if answer:
                security_question = SecurityQuestion(question=question, user=user)
                security_question.set_answer(answer)
                db.session.add(security_question)

        db.session.commit()  # Save all changes

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', security_questions=predefined_questions)


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

    if request.method == 'POST':
        # Handle adding a new vault item
        item_type = request.form.get('item_type')  # 'Login', 'Credit Card', etc.
        name = request.form.get('name')  # Friendly name for the item

        if not item_type or not name:
            flash("Item type and name are required.", "danger")
            return redirect(url_for('vault'))

        # Create and add the new VaultItem
        new_item = VaultItem(user_id=user_id, item_type=item_type, name=name)
        db.session.add(new_item)
        db.session.commit()

        # Add details for the new item
        detail_keys = request.form.getlist('detail_key')  # List of keys
        detail_values = request.form.getlist('detail_value')  # Corresponding values

        for key, value in zip(detail_keys, detail_values):
            if key and value:  # Ensure non-empty key-value pairs
                new_detail = VaultDetail(vault_item_id=new_item.id, key=key, value=value)
                db.session.add(new_detail)

        db.session.commit()
        flash("Vault item added successfully!", "success")
        return redirect(url_for('vault'))

    # Render the vault page with items and details
    return render_template('vault.html', vault_items=vault_items)

    return ui_manager.render_vault(vault_items)
    

@app.route('/generate_password', methods=['GET', 'POST'])
def generate_password():
    if request.method == 'POST':
        length = int(request.form.get('length'))
        complexity = request.form.get('complexity')
        password = PasswordBuilder().set_length(length).set_complexity(complexity).build()
        return render_template('password.html', password=password)
    return render_template('password_generator.html')


@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form['email']
        user_answers = [
            request.form['answer1'],
            request.form['answer2'],
            request.form['answer3']
        ]

        # Fetch user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('recover_password'))

        # Initialize recovery handler
        recovery_handler = RecoveryHandler()
        security_question_handler = SecurityQuestionHandler()
        recovery_handler.set_chain(security_question_handler)

        # Perform recovery
        if recovery_handler.recover(user, user_answers):
            flash("Password recovery successful! You may now reset your password.", "success")
            return redirect(url_for('reset_password', user_id=user.id))
        else:
            flash("One or more answers were incorrect. Please try again.", "danger")
            return redirect(url_for('recover_password'))

    return render_template('recovery.html')



@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log the user out
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        flash("Please log in to add items to your vault.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        item_type = request.form.get('item_type')  # 'Login', 'Credit Card', etc.
        name = request.form.get('name')  # Friendly name for the item

        if not item_type or not name:
            flash("Item type and name are required.", "danger")
            return render_template('add_item.html')

        # Create and add the new VaultItem
        new_item = VaultItem(user_id=user_id, item_type=item_type, name=name)
        db.session.add(new_item)
        db.session.commit()

        # Add details for the new item
        detail_keys = request.form.getlist('detail_key')  # List of keys
        detail_values = request.form.getlist('detail_value')  # Corresponding values

        for key, value in zip(detail_keys, detail_values):
            if key and value:  # Ensure non-empty key-value pairs
                new_detail = VaultDetail(vault_item_id=new_item.id, key=key, value=value)
                db.session.add(new_detail)

        db.session.commit()
        flash("Vault item added successfully!", "success")
        return redirect(url_for('vault'))

    # Render the item addition form for GET requests
    return render_template('add_item.html')

@app.route('/modify_item/<int:item_id>', methods=['GET', 'POST'])
def modify_item(item_id):
    if 'user_id' not in session:
        flash("Please log in to modify items in your vault.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id).first()

    if not item:
        flash("Item not found or you do not have permission to edit this item.", "danger")
        return redirect(url_for('vault'))

    if request.method == 'POST':
        # Update item details
        item.name = request.form.get('name', item.name)
        item.item

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session:
        flash("Please log in to delete items from your vault.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    item = VaultItem.query.filter_by(id=item_id, user_id=user_id).first()

    if not item:
        flash("Item not found or you do not have permission to delete this item.", "danger")
        return redirect(url_for('vault'))

    # Delete the item and its details
    VaultDetail.query.filter_by(vault_item_id=item.id).delete()
    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully!", "success")
    return redirect(url_for('vault'))


@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('recover_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('reset_password.html', user_id=user.id)

        user.set_password(new_password)  # Hash the new password
        db.session.commit()  # Save the changes
        flash("Your password has been reset successfully! You may now log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', user_id=user.id)

if __name__ == '__main__':
    app.run(debug=True)

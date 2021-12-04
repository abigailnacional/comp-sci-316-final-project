from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length
from flask_babel import _, lazy_gettext as _l

from .models.user import User
from .models.product_review import ProductReview
from .products import product_sellers

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

"""
This method allows the user to log in with a valid email and password.
If the user is already logged in, they are redirected to the home page.
If invalid information is entered, the user is notified.
After the user has logged in, they are redirected to the home page.
"""
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    first_name = StringField(_l('First Name'), validators=[DataRequired(),
        Length(min=0, max=32, message='First name must be between 0 and 32 characters in length.')])
    last_name = StringField(_l('Last Name'), validators=[DataRequired(),
        Length(min=0, max=32, message='Last name must be between 0 and 32 characters in length.')])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(),
        Length(min=0, max=64, message='Email must be between 0 and 64 characters in length.')])
    password = PasswordField(_l('Password'), validators=[DataRequired(),
        Length(min=0, max=32, message='Password must be between 0 and 32 characters in length.')])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    address = StringField(_l('Address'), validators=[DataRequired(),
        Length(min=0, max=60, message='Address must be between 0 and 60 characters in length.')])
    submit = SubmitField(_l('Register'))

    """
    This method validates whether or not the email being inputted is already
    within the database.
    """
    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))

"""
This method allows the user to register with at minimum an email, password,
and first and last name. The user may also enter an address.
"""
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.first_name.data,
                         form.last_name.data,
                         form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

"""
This method allows the user to log out of their account.
After logging out, the user is redirected to the home page.
"""
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

"""
This method allows a logged-in user to view their account information page.
"""
@bp.route('/view_account')
def view_account():
    if current_user.is_authenticated:
        return render_template('edit_acct_info/account.html')
    return redirect(url_for('users.login'))

"""
This method allows a user to view the public profile of any user, including themselves.
If the owner of the public profile is not a seller, only their account ID, first name,
and last name will be displayed on the profile page.
If the owner of the public profile is a seller, their account ID, first name, last name,
email, address, seller affiliation, and seller reviews will be displayed on the profile
page.
"""
@bp.route('/view_public_profile/<public_user_id>')
def view_public_profile(public_user_id):
    if User.check_seller(public_user_id):
        #If user is a seller, render user profile with extra seller info
        reviews = ProductReview.get_reviews(User.get_seller_info(public_user_id).id, "seller")
        summary_ratings = ProductReview.get_summary_rating(User.get_seller_info(public_user_id).id, "seller")
        return render_template(
            'public_seller_profile.html',
            seller =  User.get_seller_info(public_user_id),
            product_sellers = product_sellers,
            reviews=reviews,
            summary_ratings=summary_ratings
        )
        
    #If user is not a seller, render user profile with limited info
    return render_template(
    'public_user_profile.html',
    user = User.get(public_user_id)
    )
        
    return redirect(url_for('users.login'))

class EditEmailForm(FlaskForm):
    email = StringField(_l('New Email'), validators=[DataRequired(), Email(),
        Length(min=0, max=64, message='Email must be between 0 and 64 characters in length.')])
    submit = SubmitField(_l('Update Email'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))

@bp.route('/edit_email', methods=['GET', 'POST'])
def edit_email():
    form = EditEmailForm()
    if form.validate_on_submit():
        if User.edit_email(current_user, form.email.data):
            flash('Email has been changed.')
            return redirect(url_for('users.view_account'))
    return render_template('edit_acct_info/edit_email.html', title='Edit Email', form=form)

class EditFnameForm(FlaskForm):
    first_name = StringField(_l('First Name'), validators=[DataRequired(),
        Length(min=0, max=32, message='First name must be between 0 and 32 characters in length.')])
    submit = SubmitField(_l('Update First Name'))

@bp.route('/edit_fname', methods=['GET', 'POST'])
def edit_fname():
    form = EditFnameForm()
    if form.validate_on_submit():
        if User.edit_fname(current_user, form.first_name.data):
            flash('First name has been changed.')
            return redirect(url_for('users.view_account'))
    return render_template('edit_acct_info/edit_fname.html', title='Edit First Name', form=form)

class EditLnameForm(FlaskForm):
    last_name = StringField(_l('Last Name'), validators=[DataRequired(),
        Length(min=0, max=32, message='Last name must be between 0 and 32 characters in length.')])
    submit = SubmitField(_l('Update Last Name'))

@bp.route('/edit_lname', methods=['GET', 'POST'])
def edit_lname():
    form = EditLnameForm()
    if form.validate_on_submit():
        if User.edit_lname(current_user, form.last_name.data):
            flash('Last name has been changed.')
            return redirect(url_for('users.view_account'))
    return render_template('edit_acct_info/edit_lname.html', title='Edit Last Name', form=form)

class EditAddressForm(FlaskForm):
    address = StringField(_l('Address'), validators=[DataRequired(),
        Length(min=0, max=60, message='Address must be between 0 and 60 characters in length.')])
    submit = SubmitField(_l('Update Address'))

@bp.route('/edit_address', methods=['GET', 'POST'])
def edit_address():
    form = EditAddressForm()
    if form.validate_on_submit():
        if User.edit_address(current_user, form.address.data):
            flash('Address has been changed.')
            return redirect(url_for('users.view_account'))
    return render_template('edit_acct_info/edit_address.html', title='Edit Address', form=form)

class EditPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired(),
        Length(min=0, max=32, message='Password must be between 0 and 32 characters in length.')])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Update Password'))

@bp.route('/edit_password', methods=['GET', 'POST'])
def edit_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        if User.edit_password(current_user, form.password.data):
            flash('Password has been changed.')
            return redirect(url_for('users.view_account'))
    return render_template('edit_acct_info/edit_password.html', title='Edit Password', form=form)

class EditBalanceForm(FlaskForm):
    amount = FloatField(_l('Amount to Withdraw/Deposit'), 
        validators=[DataRequired(message='Please enter a number.'),
        NumberRange(min=0, max=1000000000.1, 
        message='You must enter a number between 0 and 1000000000 (1 billion).')])
    submit = SubmitField(_l('Update Balance'))

@bp.route('/decrement_balance', methods=['GET', 'POST'])
def decrement_balance():
    form = EditBalanceForm()
    if form.validate_on_submit():
        if User.has_enough_money(current_user, form.amount.data):
            if User.decrement_balance(current_user, form.amount.data):
                flash('Money has been withdrawn from your account.')
                return redirect(url_for('users.view_account'))
        flash('You do not have enough money in your account!')
    return render_template('edit_acct_info/withdraw_money.html', title='Withdraw Money', form=form)

@bp.route('/increment_balance', methods=['GET', 'POST'])
def increment_balance():
    form = EditBalanceForm()
    if form.validate_on_submit():
        if User.under_max_balance(current_user, form.amount.data):
            if User.increment_balance(current_user, form.amount.data):
                flash('Money has been deposited into your account.')
                return redirect(url_for('users.view_account'))
        flash('Your account will exceed the maximum balance if this amount is deposited.')
    return render_template('edit_acct_info/deposit_money.html', title='Deposit Money', form=form)

from flask import render_template, redirect, url_for
from flask_login import current_user
from typing import List
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, TextField, IntegerField, DecimalField, SelectMultipleField, FileField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l

from .models.inventory import InventoryEntry
from .models.coupon import Coupon


from flask import Blueprint

bp = Blueprint('inventory', __name__)


@bp.route('/inventory')
def inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    items: List[InventoryEntry] = InventoryEntry.get_all_entries_by_seller(
        seller_id=current_user.id)

    coupons = {}
    for item in items:
        coupon = Coupon.get_current_coupon_for_product_seller(item.product_id, item.seller_id)
        if coupon:
            coupons[item.product_id] = coupon.code

    return render_template(
        'products_sold.html', 
        inventory=items,
        coupons=coupons
    )

@bp.route('/inventory/increment_quantity/<id>', methods=['POST'])
def increment_quantity(id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    InventoryEntry.increase_quantity(id, current_user.id)


    return redirect(url_for('inventory.inventory'))


@bp.route('/inventory/decrement_quantity/<id>', methods=['POST'])
def decrement_quantity(id):
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))
    
    InventoryEntry.decrease_quantity(id, current_user.id)

    return redirect(url_for('inventory.inventory'))


@bp.route('/inventory/delete_product/<id>', methods=['POST'])
def delete_product(id):
    """
    Marks the Sells.is_available = false for this seller/item.
    """

    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    InventoryEntry.delete_item(id, current_user.id)

    return redirect(url_for('inventory.inventory'))

class AddProductForm(FlaskForm):
    name = StringField(_l('Product Name'), validators=[DataRequired()])
    description = StringField(_l('Product Description'))
    price = DecimalField(_l('Product Price'), validators=[DataRequired()])
    category = SelectField(_l('Type'),
        choices = [('', 'Select a category'), ('Entrées', 'Entrées'), ('Sides', 'Sides'), ('Appetizers', 'Appetizers'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages')],
        validators=[DataRequired()]
    )
    # have to input restaurant id as string for flask form constraints (later convert back to int for sql query)
    restaurant = RadioField(_l('Locations Served'),
        choices = [('1', 'Beyu Blue'), ('2', 'The Loop'), ('3', 'McDonalds'), ('4', 'Panda Express'), ('5', 'Il Forno'), ('6', 'Sazon')],
        validators=[DataRequired()]
    )
    inventory = IntegerField(_l('Product Inventory'), validators=[DataRequired()])
    image = FileField(_l('Product Image'), validators=[DataRequired()])
    submit = SubmitField(_l('Start Selling Product'))


@bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        #if InventoryEntry.add_product(current_user, form.name.data, form.id.data, form.description.data, form.price.data,
        #                              form.inventory.data, form.category.data, form.restaurant.data):
        #    flash('Product has been added!')
        #    return redirect(url_for('inventory.inventory'))
        return redirect(url_for('inventory.inventory'))
    print(form.errors)
    return render_template('add_product.html', form=form)



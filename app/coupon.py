from flask_login import current_user
from flask import redirect, url_for, request

from .models.coupon import Coupon
from flask import Blueprint


bp = Blueprint('coupon', __name__)

"""
This method generates a new coupon for a specific product from a specific seller
"""
@bp.route('/generate_coupon/<product_id>/<seller_id>')
def generate_coupon(product_id, seller_id):
    if current_user.is_authenticated:
        if not Coupon.get_current_coupon_for_product_seller(product_id, seller_id):
            Coupon.generate_new_coupon(product_id, seller_id)
        return redirect(request.referrer)
    return redirect(url_for('users.login'))

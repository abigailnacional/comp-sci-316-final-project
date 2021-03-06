from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request

from .models.product import Product
from .models.product_review import ProductReview
from .models.user import User

from flask import Blueprint
bp = Blueprint('products', __name__)

product_sellers = {1: 'Beyu Blue', 2: 'The Loop', 3: 'McDonalds', 4: 'Panda Express', 5: 'Il Forno',
                   6: 'Sazón'}

@bp.route('/product', methods=['GET'])
def view_product():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    products = Product.get_specific(vender_id, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/product?id=" + str(vender_id) + "&page=", max_pages=len(products))

@bp.route('/filter', methods=['GET'])
def filtered_cat():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    spec_category = request.args.get('cat')
    products = Product.filteredCat(vender_id, spec_category, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/filter?id=" + str(vender_id) + "&cat=" + spec_category + "&page=", max_pages=len(products))

@bp.route('/filter-price', methods=['GET'])
def filtered_price():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    products = Product.filteredPrice(vender_id, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/filter-price?id=" + str(vender_id) + "&page=", max_pages=len(products))  

@bp.route('/filter-rat', methods=['GET'])
def filtered_rating():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    stars = int(request.args.get('stars'))
    products = Product.filteredRating(stars, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/filter-rat?id=" + str(vender_id) + "&stars=" + str(stars) + "&page=", max_pages=len(products)) 

@bp.route('/search', methods=['GET'])
def search_filter():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    search = request.args.get('search')
    products = Product.search_filter(search, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/search?id=" + str(vender_id) + "&search=" + search + "&page=", max_pages=len(products))   

@bp.route('/id-search', methods=['GET'])
def search_id():
    vender_id = int(request.args.get('id'))
    page_num = int(request.args.get('page'))
    search = request.args.get('search')
    products = Product.search_id(search, page_num)
    categories = Product.get_categories()
    average_ratings = ProductReview.get_average_rating([product.id for product in products], "product")
    return render_template('product.html', vender_id=vender_id, product_sellers=product_sellers, 
                            avail_products=products, categories=categories, average_ratings=average_ratings,
                            page_num=page_num, pag_tag="/id-search?id=" + str(vender_id) + "&search=" + search + "&page=", max_pages=len(products))  

@bp.route('/view', methods=['GET'])
def ind_view():
    prod_id = int(request.args.get('id'))
    product = Product.get(prod_id)
    sellers = User.get_sellers(prod_id)
    reviews = ProductReview.get_reviews(prod_id, "product")
    summary_ratings = ProductReview.get_summary_rating(prod_id, "product")
    upvote_exists, user_product_reports = [], []
    if current_user.is_authenticated:
        upvote_exists = [ProductReview.check_upvote_exists(current_user.id, review.reviewer_id, prod_id, -1) for review in reviews]
        user_review_reports = ProductReview.get_user_review_reports(current_user.id)
        user_product_reports = [(user_review_report[1], user_review_report[2]) for user_review_report in user_review_reports]
    return render_template('ind_prod.html', product_info=product, sellers=sellers, 
                            product_sellers=product_sellers, reviews=reviews,
                            summary_ratings=summary_ratings, upvote_exists=upvote_exists,
                            user_product_reports=user_product_reports)
    


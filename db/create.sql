-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

/* Users schema
id: randomly generated unique identifier (int)
email: gmail account created through random string generation (varchar)
password: account password created through random string generation (varchar)
first_name and last_name: user identifier generated through Python names module (varchar)
balance: represents current account balance - default at 0 with checks to ensure never becomes neg (float)
address: mailing address for user generated through random_address module (varchar)*
*defaults to home address for all students, employees, etc. 
*/
CREATE TABLE Users (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    balance FLOAT DEFAULT 0.00,
    address VARCHAR(255),
    CHECK (balance >= 0.00)
);

/* Product schema
id: randomly generated unique identifier (int)
name: name of product (varchar)
description: longer description of product features, ingredients, allergies (varchar)
category: type of product - one of Appetizers, Entrées, Sides, Desserts, Beverages (varchar)
price: product price (decimal)
is_available: whether product is currently available for purchase (boolean)
creator_id:
image: link to the product image (varchar)
*/
CREATE TABLE Product (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255), /* changed from not null */
    category VARCHAR(255) NOT NULL,
    price FLOAT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    creator_id INT NOT NULL,
    image VARCHAR(255) NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES Users(id),
    CHECK (category IN ('Appetizers', 'Entrées', 'Sides', 'Desserts', 'Beverages'))
    /* ensures category falls within one of the predetermined types */
    
);

CREATE TABLE Sells (
   seller_affiliation INT NOT NULL,
   seller_id INT NOT NULL,
   product_id INT NOT NULL,
   inventory INT NOT NULL,
   is_available BOOLEAN NOT NULL DEFAULT TRUE,
   FOREIGN KEY (seller_id) REFERENCES Users(id),
   FOREIGN KEY (product_id) REFERENCES Product(id),
   PRIMARY KEY (seller_id, product_id)
);

/* Coupon schema
code: unique string that represents the coupon code to use
expiration_date: the time at which the coupon is no longer valid
product_id: the product for which this coupon applies
seller_id: the seller for which this coupon applies
percent_off: the percent off the product the coupon gives
*/
CREATE TABLE Coupon (
    code VARCHAR(255) PRIMARY KEY,
    expiration_date timestamp without time zone NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    percent_off INT NOT NULL,
    FOREIGN KEY (seller_id, product_id) REFERENCES Sells(seller_id, product_id) ON DELETE CASCADE,
    CHECK (percent_off > 0 AND percent_off <= 100)
);

/* Cart schema
id: randomly generated unique identifier (int)
user_id: the user who the cart belongs to
is_current: whether or not this cart is currently used or is a past order
time_purchased: the time at which the cart was purchased (initially null)
is_fulfilled: whether or not the cart, as an order, has been fulfilled (initially False)
coupon_applied: an optional field that stores a the coupon code applied if one exists
*/
CREATE TABLE Cart (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    time_purchased timestamp without time zone DEFAULT NULL,
    is_fulfilled BOOLEAN DEFAULT FALSE,
    coupon_applied VARCHAR,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (coupon_applied) REFERENCES Coupon(code)
);

/* ProductInCart schema
id: randomly generated unique identifier (int)
cart_id: the cart the product is in
product_id: the product in the cart
seller_id: the seller of the product in the cart
quantity: the amount of the product that is in the cart
*/
CREATE TABLE ProductInCart (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES Cart(id),
    FOREIGN KEY (seller_id, product_id) REFERENCES Sells(seller_id, product_id) ON DELETE CASCADE
);

/* Purchase schema
product_in_cart_id: the id of the product in cart that this purchase links to
user_id: the user who made this purchase
time_purchased: the time at which the purchase was made
is_fulfilled: whether or not the purchase, has been fulfilled by the seller (initially False)
time_of_fulfillment: the time at which the purchase was fulfilled
cart_id: the id of the cart this purchase was in
final_unit_price: the price for which the user bought each unit
*/
CREATE TABLE Purchase (
    product_in_cart_id INT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    is_fulfilled BOOLEAN DEFAULT FALSE,
    time_of_fulfillment timestamp without time zone DEFAULT NULL,
    cart_id INT NOT NULL,
    final_unit_price FLOAT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES Cart(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (product_in_cart_id) REFERENCES ProductInCart(id) ON DELETE CASCADE
);

CREATE TABLE Feedback (
    reviewer_id INT NOT NULL,
    rating INT NOT NULL,  -- this should be 1 - 5
    review VARCHAR(255) NOT NULL,
    product_id INT,
    seller_id INT,
    time_posted timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    upvotes INT NOT NULL DEFAULT 0,
    reports INT NOT NULL DEFAULT 0,
    PRIMARY KEY (reviewer_id, product_id, seller_id),
    FOREIGN KEY (reviewer_id) REFERENCES Users(id),
    FOREIGN KEY (seller_id) REFERENCES Users(id),
    FOREIGN KEY (product_id) REFERENCES Product(id),
    CHECK((product_id IS NOT NULL) OR (seller_id IS NOT NULL))
);

CREATE TABLE Feedback_Upvotes (
    upvoter_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    product_id INT,
    seller_id INT,
    PRIMARY KEY (upvoter_id, reviewer_id, product_id, seller_id),
    FOREIGN KEY (upvoter_id) REFERENCES Users(id),
    FOREIGN KEY (reviewer_id) REFERENCES Users(id),
    FOREIGN KEY (product_id) REFERENCES Product(id),
    FOREIGN KEY (seller_id) REFERENCES Users(id),
    CHECK((product_id IS NOT NULL) OR (seller_id IS NOT NULL))
);

CREATE TABLE Feedback_Reports (
    reporter_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    product_id INT,
    seller_id INT,
    PRIMARY KEY (reporter_id, reviewer_id, product_id, seller_id),
    FOREIGN KEY (reporter_id) REFERENCES Users(id),
    FOREIGN KEY (reviewer_id) REFERENCES Users(id),
    FOREIGN KEY (product_id) REFERENCES Product(id),
    FOREIGN KEY (seller_id) REFERENCES Users(id),
    CHECK((product_id IS NOT NULL) OR (seller_id IS NOT NULL))
);

CREATE INDEX PRODUCT_IN_CART_CART_ID_INDEX ON ProductInCart(cart_id);
CREATE INDEX PURCHASE_CART_ID_INDEX ON Purchase(cart_id);

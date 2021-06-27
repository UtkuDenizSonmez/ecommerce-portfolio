from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_bootstrap import Bootstrap
from forms import LoginForm, RegisterForm, ItemForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import os


app = Flask(__name__)
Bootstrap(app)


# app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SECRET_KEY"] = "213123123sdfgdrgerşierwlşiwüüü,,ü"

uri = os.environ.get("DATABASE_URL", "sqlite:///ecommerce.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# CONNECT DB
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    # ADD ITEMS. MAKE IT RELATION WITH ITEM TABLE.

    purchases = relationship("Purchase", back_populates="purchaser")


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    supply = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    photo_url = db.Column(db.Integer, nullable=False)
    # Parent
    purchase = relationship("Purchase", back_populates="item")


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    paid = db.Column(db.Boolean, nullable=False)

    # Relationships
    purchaser_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    purchaser = relationship("User", back_populates="purchases")

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    item = relationship("Item", back_populates="purchase")


db.create_all()


@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    all_items = Item.query.paginate(page=page, per_page=8, error_out=True)
    return render_template("index.html", all_items=all_items)


@app.route("/items/<string:q>")
def selected_query(q):
    # Different queries for dropdown menu items.
    # When admin entering items, enter jeans or trousers as trousers, Shoes as Shoes, T-shirt, Watch.
    # (Can be added more.)
    query = q.split("_")
    all_items = Item.query.filter_by(type=query[1].title(), sex=query[0].title())
    return render_template("selected-query.html", all_items=all_items)


@app.route("/my-bag")
def my_bag_page():
    # Add bagged_item to cart
    if current_user.is_anonymous:
        redirect(url_for("login"))

    in_cart = db.session.query(Purchase).filter(Purchase.purchaser_id == current_user.id, Purchase.paid is not True)
    in_cart = [pur.item_id for pur in in_cart]
    products_in_cart = [product for product in Item.query.all() if product.id in in_cart]
    total_price = 0
    for product in products_in_cart:
        total_price += product.price
    return render_template("my-bag.html", purchases=products_in_cart, total=total_price)


@app.route("/to-bag")
def add_item_to_bag():
    item_id = request.args.get("item_id")
    if not current_user.is_anonymous:
        existing_purchase = db.session.query(Purchase).filter(Purchase.item_id == item_id).first()
        print(existing_purchase)
        if not existing_purchase:
            # Add new purchase
            purchase = Purchase(paid=False, purchaser_id=current_user.get_id(), item_id=item_id)
            # If The item purchased(paid=True):
                # Do This
                # item = Item.query.filter_by(id=item_id).first()
                # item.supply -= 1
            db.session.add(purchase)
            db.session.commit()
            flash("Thanks for shopping!")
            return redirect(url_for("home"))
        flash("Sorry, that product has already in your cart.", "error")
        return redirect(url_for("home"))
    flash("You need to log in to start shopping.", "error")
    return redirect(url_for('login'))


@app.route("/delete-from-bag")
def delete_from_bag():
    item_id = request.args.get("item_id")
    purchase = db.session.query(Purchase).filter(Purchase.item_id == item_id).first()
    if purchase:
        db.session.delete(purchase)
        db.session.commit()
    return redirect(url_for("my_bag_page"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get the Data from forms.
        user_email = form.email.data
        user_pass = form.password.data

        # Get the user with same email in the form.
        user = User.query.filter_by(email=user_email).first()
        # Check if user exist
        if user:
            # Check the user's password equals to password in form
            if check_password_hash(user.password, user_pass):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Incorrect Password or Email. Please try again.")
                return redirect(url_for("login"))
        else:
            flash("There is no user with that email.")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and form.validate():
        hashed_and_salted_password = generate_password_hash(
            password=form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Thank you for Registering (:")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect(url_for("home"))


@app.route("/add-item", methods=["GET", "POST"])
@admin_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        filename = secure_filename(form.photo.data.filename)
        form.photo.data.save('static/uploads/' + filename)

        new_item = Item(
            name=form.name.data.title(),
            sex=form.sex.data.title(),
            type=form.type.data.title(),
            price=form.price.data,
            supply=form.supply.data,
            size=form.size.data.title(),
            photo_url='static/uploads/' + filename
        )
        # Add item to DB
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("add_item"))

    return render_template("add-item.html", form=form)


@app.route("/add-item/<int:item_id>")
def selected_item(item_id):

    requested_item = Item.query.get(item_id)
    return render_template("selected-item.html", requested_item=requested_item)


@app.route("/delete-item/<int:item_id>")
@admin_required
def delete_item(item_id):

    item_to_delete = Item.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    flash("Item is deleted successfully !")
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)



import flask
from flask_login.utils import logout_user
from stripe.api_resources import checkout
from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, addproductForm
from market import db
from flask import jsonify
from flask_login import login_user, logout_user, login_required, current_user
import stripe

app.config['STRIPE_PUBLIC_KEY'] ='pk_test_51JIPoAI0cnKL5Y8unE4rvCbdVrLNs8h8hVaXxLn4vA0JddWR3HE8q7Jmj9mQKKdRV1EMJoxBwCBWf3iofmJksiyo004feqriXr'
app.config['STRIPE_SECRET_KEY'] ='sk_test_51JIPoAI0cnKL5Y8uK2w2sa8cTXJd1yENUW2XPVuR72DEQSV6gmKVOktxPJBxdAMg4Gkbe1kB7WO64D9TqMLHcmzz00rlZNftQG'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/') 
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()

        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                        'name': p_item_object.name,
                        },
                        'unit_amount': int(p_item_object.price) * 100
                    },
                    'quantity': 1,
                    }],
                    mode='payment',
                    success_url='https://it-mark.herokuapp.com/success',
                    cancel_url='https://it-mark.herokuapp.com/failure',
                )
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')

                return redirect(session.url, code=303)
            else:
                flash(f"Unfortunately, you don't have enough budget for this purchase {p_item_object.name}!", category='danger')
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')


        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)




@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    form = addproductForm()
    if form.validate_on_submit():
        item_to_create = Item(name=form.name.data,
                              price=form.price.data,
                              barcode=form.barcode.data,
                              description=form.description.data,
                              )
        db.session.add(item_to_create)
        db.session.commit()
        flash(f"Item added successfully! Item {item_to_create.name}", category='success')
        return redirect(url_for('admin_page'))
    if form.errors != {}: #If there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error adding item: {err_msg}', category='danger')

    return render_template('add_products.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            
            login_user(attempted_user)

            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        


        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/search/<query>', methods=['GET'])
def getSearch(query):
    new_list = []
    char = '*','#','&'
    if request.method == 'GET':
        search = query
        for cha in char:
            if cha in search:
                raise TypeError
            
            else:
                all_items = [item.to_json() for item in Item.query.all()]
                
            for item in all_items:
                if search.lower() in (item['name'].lower() or item['description'].lower()):
                    new_list.append(item)
        return jsonify(new_list)


@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            
            login_user(attempted_user)
            if attempted_user.username == 'admin':
                return redirect(url_for('admin_page'))
            else:
                flash('You are not allowed to view this page')
    return render_template('login.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    return render_template('admin.html')

@app.route('/success', methods=['GET', 'POST'])
def success_page():
    return render_template('success.html')

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

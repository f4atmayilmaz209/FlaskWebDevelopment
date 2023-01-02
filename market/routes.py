from market import app
from flask import render_template,redirect,url_for,flash,get_flashed_messages,request
from market.models import Wtem,User
from market.forms import RegisterForm,LoginForm,PurchaseForm,SellItemForm
from market import db
from flask_login import login_user,logout_user,login_required,current_user

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')


@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    purchase_form=PurchaseForm()
    selling_form=SellItemForm()
    if request.method=="POST":
        purchase_item=request.form.get('purchase_item')
        p_item_object=Wtem.query.filter_by(name=purchase_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations!You purchased {p_item_object.name}")
            else:
                flash(f"Unfortunatelly,you dont have enough money to purchase{p_item_object.name}")
        sold_item=request.form.get('sold_item')
        s_item_project=Wtem.query.filter_by(name=sold_item).first()
        if s_item_project:
            if current_user.can_sell(s_item_project):
                s_item_project.sell(current_user)
                flash(f"Congratulations! you sold {s_item_project.name} back to market!",category='success')
            else:
                flash(f"Something went wrong with selling {s_item_project.name}",category='danger')

        return redirect(url_for('market_page'))
    if request.method=="GET":
        items = Wtem.query.filter_by(owner=None)
        owned_items=Wtem.query.filter_by(owner=current_user.id)
        return render_template('market.html',items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form)


@app.route('/register',methods=['GET','POST'])
def register_page():
    form=RegisterForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data,email=form.email.data,password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully!You are now logged in as {user_to_create.username}",category='success')
        return redirect(url_for('market_page'))
    
    if form.errors!={}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user:{err_msg}',category='danger')


    return render_template('register.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("you have been logged out!",category='info')
    return redirect(url_for("home_page"))

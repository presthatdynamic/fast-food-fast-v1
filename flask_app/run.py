"""
This is the entry point for the app
"""

import os
from flask import request, redirect, url_for,\
    render_template, flash
from app import create_app
from app.models import db
from app import controller

config_name = os.getenv('APP_SETTINGS') or 'development'
app = create_app(config_name)
    

# routes
@app.route('/')
def index():
    """
    The homepage comprising signup and signin options
    """
    active = 'home'
    return render_template('index.html', active=active)


@app.route('/signup', methods=['POST'])
def signup():
    """
    The signup route handles POST data sent from 
    the signup form on the home/index page
    """
    error = None
    form_data = None
    try:
        required_keys = ('first_name', 'last_name', 'email', 'password')
        form_data = controller.process_form_data(dict(request.form),
                                                 *required_keys)
    except (AttributeError, ValueError):
        error = 'invalid request'
    if form_data:
        # get the data and attempt to create a new user
        try:
            user = db.create_user(form_data)            
        except ValueError as e:
            # error = 'Invalid form input'
            error = str(e)
        else:
            # if new user is created, log them in
            try:
                controller.add_user_to_session(user.key)
            except KeyError:
                error = 'Error while logging in'
            else:
                # redirect the user to dashboard
                flash('User sign up successful')
                return redirect(url_for('orders_list',
                                user_key=user.key))
    if error:
        flash(error)
    return redirect(url_for('index'))



@app.route('/signout')
def signout():
    """
    The signout route logs out the user
    """
    error = None
    # remove user_key from session
    try:
        controller.remove_user_from_session()
    except KeyError:
        error = 'You are not logged in'
    if error:
        flash(error)
    return redirect(url_for('index'))


@app.route('/signin', methods=['POST'])
def signin():
    """
    Logs in the user
    """
    error = None
    form_data = None
    # get request.form data
    try:
        required_keys = ('email', 'password')
        form_data = controller.process_form_data(dict(request.form), *required_keys)
    except (AttributeError, ValueError):
        error = "Invalid form input"
    
    if form_data:
        try:
            user = db.get_user_by_email(form_data['email'])
            if user is None:
                raise KeyError('User non-existent')
        except KeyError:
            error = "User does not exist"
        else:
            # if user exists, check against the saved password
            if user.password == form_data['password']:
                # if it is the same, save username to session
                controller.add_user_to_session(user.key)
                flash('Login successful')
                return redirect(url_for('orders_list',
                                user_key=user.key))
            else:
                error = "Invalid password or username"
    if error:
        flash(error)
    return redirect(url_for('index'))


@app.route('/user/<int:user_key>/orders', methods=['GET', 'POST'])
def orders_list(user_key):
    """
    The page showing all availaible orders of orders
    GET: Show all user's orders
    POST: Create a new category
    """
    active = 'orders_list'
    error = None
    editable = False
    order_categories = []
    user_details = {}
    user = None
    # try to get the user
    try:
        user = db.get_user(int(user_key))
        if user:
            user_details = dict(first_name=user.first_name, email=user.email,
            last_name=user.last_name, key=user.key)
            order_categories = user.get_all_order_categories(db)
            # try to get the logged in user
            logged_in_user_key = controller.get_logged_in_user_key()
            if logged_in_user_key == user.key:
                # a registered user should be able to edit/create orders
                editable = True
    except (KeyError, TypeError):
        error = "User does not exist"

    if request.method == 'POST' and not error:
        # Get the form data
        form_data = None
        try:
            required_keys = ('name',)
            form_data = controller.process_form_data(dict(request.form),
                                                     *required_keys)
        except (AttributeError, ValueError):
            error = "Invalid form input"
        else:
            # Try to create a new order category and add it to order category list
            new_category = user.create_order_category(db, form_data)
            if new_category:
                order_categories.append(new_category)

    return render_template('orders_list.html', active=active, error=error,
                            user_details=user_details, editable=editable,
                            order_categories=order_categories)


@app.route('/user/<int:user_key>/orders/<int:category_key>',
           methods=['GET', 'POST'])
def categories_detail(user_key, category_key):
    """
    The page showing all availaible orders in a given category (GET)
    Also handles PUT and DELETE of a order category
    Allows creation of new orders under this category(POST)
    """
    error = None
    editable = False
    order_category_details = {}
    order_category = None
    orders = []
    user = None
    missing_required_field = False
    try:
        order_category = db.get_order_category(category_key)
        if order_category and user_key == order_category.user:
            if user_key == controller.get_logged_in_user_key():
                editable = True
        else:
            raise ValueError('Wrong params in url')
    except (ValueError, KeyError, AttributeError):
        error = "order Category does not exist"  

    if request.method == 'GET':
        method = request.args.get('_method') or None
        if editable and method == 'delete' and order_category:
            # attempt to delete the order_category
            order_category.delete(db)
            flash('Delete successful')
            return redirect(url_for('orders_list', user_key=user_key))
        
        if editable and method == 'put' and order_category:
            # get args data
            success = None
            try:
                form_data = controller.process_args_data(request.args, 'name')
            except ValueError as e:
                flash(str(e))
                missing_required_field = True
            
            description = request.args.get('description') or None
            name = request.args.get('name') or None
            if name and not missing_required_field:
                # update the name
                order_category.set_name(str(name), db)
                success = "Update successful"
            if description:
                # update the description
                order_category.set_description(str(description), db)
                success = "Update successful"
            flash(success)
            return redirect(url_for('orders_list', user_key=user_key))            
        
        if not error:
            order_category_details = dict(name=order_category.name,
                            description=order_category.description, 
                            key=order_category.key)
            orders = list(order_category.get_all_orders(db))
        return render_template('categories_detail.html', 
                order_category_details=order_category_details, user_key=user_key,
                 editable=editable, error=error, orders=orders, category_key=category_key)

    if request.method == 'POST' and not error:
        # get form data
        form_data = None
        try:
            required_keys = ('name',)
            form_data = controller.process_form_data(dict(request.form),
                                                     *required_keys)
        except (AttributeError, ValueError):
            error = "Invalid form input"
            flash(error)
    
        if form_data:
            try:
                order_category.create_order(db, form_data)
            except ValueError:
                error = "Invalid form input for order"
                flash(error)
            else:
                flash('order has been added successfully')

            return redirect(url_for('categories_detail', user_key=user_key,
                                category_key=category_key))
  
    return redirect(url_for('categories_detail', user_key=user_key,
                                category_key=category_key))


@app.route('/user/<int:user_key>/orders/<int:category_key>/orders/<int:order_key>',
methods=['POST', 'GET'])
def order_detail(user_key, category_key, order_key):
    """
    The page showing the details of a single order 
    including all steps (GET)
    It also handles PUT and DELETE of the order
    It also handles POST for creation of new orderSteps
    """
    error = None
    editable = False
    order_details = {}
    order = None
    steps = []
    user = None
    category = None
    missing_required_field = False
    try:
        order = db.get_order(order_key)
        if order:
            category = db.get_order_category(category_key)
            if category.key == order.category and user_key == category.user:
                editable = user_key == controller.get_logged_in_user_key()

    except (ValueError, KeyError, AttributeError):
        error = "order does not exist" 

    if request.method == 'GET':
        method = request.args.get('_method') or None
        if editable and method == 'delete' and order:
            # attempt to delete the order
            order.delete(db)
            flash('Delete successful')
            return redirect(url_for('categories_detail',
                            user_key=user_key, category_key=category_key))
        
        if editable and method == 'put' and order:
            # get args data
            success = None
            try:
                controller.process_args_data(request.args, 'name')
            except ValueError as e:
                flash(str(e))
                missing_required_field = True

            description = request.args.get('description') or None
            name = request.args.get('name') or None
            if name and not missing_required_field:
                # update the name
                order.set_name(str(name), db)
                success = "Update successful"
            if description:
                # update the description
                order.set_description(str(description), db)
                success = "Update successful"
            flash(success)
            return redirect(url_for('categories_detail', user_key=user_key,
                            category_key=category_key))            
        
        if not error:
            order_details = dict(name=order.name,
                            description=order.description, 
                            key=order.key)
            steps = list(order.get_all_steps(db))
        return render_template('order_detail.html', 
                order_details=order_details, user_key=user_key, category=category,
                 editable=editable, error=error, steps=steps)

    if request.method == 'POST' and not error:
        # get form data to create a new step
        form_data = None
        try:
            required_keys = ('text_content',)
            form_data = controller.process_form_data(dict(request.form), *required_keys)
        except (AttributeError, ValueError):
            error = "Invalid form input"
            flash(error)
            return redirect(url_for('order_detail', user_key=user_key,
                                category_key=category_key, order_key=order_key))
    
        if form_data:
            try:
                order.create_step(db, form_data)
            except ValueError:
                error = "Invalid form input for step"
                flash(error)
            else:
                flash('order step has been added successfully')

            return redirect(url_for('order_detail', user_key=user_key,
                                category_key=category_key, order_key=order_key))

    return redirect(url_for('order_detail', user_key=user_key,
                                category_key=category_key, order_key=order_key))


@app.route('/user/<int:user_key>/orders/\
<int:category_key>/orders/<int:order_key>/steps/<int:step_key>', methods=['GET'])
def step_detail(user_key, category_key, order_key, step_key):
    """
    Handles the DELETE and PUT of order steps but never renders to screen
    """
    error = None
    editable = False
    order_step = None
    order = None
    user = None
    category = None
    missing_required_field = False
    try:
        order_step = db.get_order_step(step_key)
        if order_step:
            order = db.get_order(order_key)
            category = db.get_order_category(category_key)
            if category.key == order.category \
            and user_key == category.user \
            and order_step.order == order_key:
                editable = user_key == controller.get_logged_in_user_key()

    except (ValueError, KeyError, AttributeError):
        error = "order step does not exist"

    if request.method == 'GET':
        method = request.args.get('_method') or None
        if editable and method == 'delete' and order_step:
            # attempt to delete the order step
            order_step.delete(db)
            flash('Delete successful')
            return redirect(url_for('order_detail', order_key=order_key,
                            user_key=user_key, category_key=category_key))
        
        if editable and method == 'put' and order_step:
            # get args data
            success = None
            try:
                controller.process_args_data(request.args, 'text_content')
            except ValueError as e:
                flash(str(e))
                missing_required_field = True

            text_content = request.args.get('text_content') or None
            if text_content and not missing_required_field:
                # update the text_content
                order_step.set_text_content(str(text_content), db)
                success = "Update successful"
            flash(success)
            return redirect(url_for('order_detail', user_key=user_key,
                            category_key=category_key, order_key=order_key)) 
    flash(error)
    # redirect to order_detail page if accessed directly                        
    return redirect(url_for('order_detail', user_key=user_key,
                            category_key=category_key, order_key=order_key))           
    

if __name__ == '__main__':
    app.run()
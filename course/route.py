from course import db
from course import app
from course.models import Items, Users
from flask import render_template, url_for, redirect, flash, request
from course.forms import RegistrForm, LoginForm, GetLinkForm, AddLinkForm, AssignTokensForm
from flask_login import login_user, logout_user, login_required, current_user
from course.admin import AdminPanel

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    display_link = GetLinkForm()
    
    '''
    request object helps different types of requests
    '''

    # we need to differenciate between GET & POST request for better optimization
    if request.method == "POST":
        if display_link.validate_on_submit():
            course_link = request.form.get('display_link')
            course_link_query_obj = Items.query.filter_by(url=course_link).first()
            
            if course_link_query_obj:
                if current_user.can_purchase(course_link_query_obj):
                    course_link_query_obj.will_be_owned(current_user)

                    flash('You have successfully bought the course', category='success')
                    return redirect(url_for('courses'))
                
                else:
                    flash(f'There is a problem processing your request', category='info')

            return redirect(url_for('courses'))
    
    if request.method == "GET":
        # Items.query.all() returnes all the rows from Items table
        items = Items.query.all()
        
        return render_template('courses.html', items=items, display_link=display_link)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # here we are storing form's fetched data to our users table.
            register_user = Users(
                username= form.username.data,
                email_address= form.email.data,
                # this will call @password.setter function
                password= form.password.data
            )
            
            db.session.add(register_user)
            db.session.commit()

            # logs in the user
            login_user(register_user)
            # redirecting the user to courses page. url_for() takes dynamic route name (function names of the rotues)
            return redirect(url_for('courses'))
        
        # .errors is a dict, it contains errors if occured. empty otherwise.
        if form.errors != {}:
            for error in form.errors.values():
                flash(f"There was some Error with User Registration: {error}", category='danger')
            
            return redirect(url_for('register'))

    if request.method == "GET":
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = Users.query.filter_by(username=form.username.data).first()

        if attempted_user and attempted_user.password_checking(attempted_password=form.password.data): 
            # logges in the user object and store its id (primary key) internally for session management
            login_user(attempted_user)
            flash(f"user logged In as: {attempted_user.username}", category='success')
            return redirect(url_for('courses'))
        
        else:
            flash("Username & Password didn't matched! Please try again later!", category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    # logs out the current user
    logout_user()
    flash("User is logged out!", category='info')
    return redirect(url_for('home'))



@app.route('/users', methods=['GET', 'POST'])
def users():
    form = AddLinkForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # if the course is already present in the database, dont let the user add it.
            is_course_present = Items.query.filter_by(name=form.course_name.data).first()
            
            if not is_course_present:
                course_upload = Items(
                    name=form.course_name.data,
                    uploader=current_user.username, 
                    url=form.course_url.data, 
                    token=form.token_worth.data, 
                    description=form.description.data
                )

                db.session.add(course_upload)
                db.session.commit()

                flash("Success! Course has been added!", category='success')
            
            else:
                flash("Course is already added by someone else. check courses page!", category='info')
            
            return redirect(url_for('users'))

        else:
            flash("There was some Error with adding the Course!", category='danger')
            return redirect(url_for('users'))

    if request.method == 'GET':
        return render_template('user.html', form=form)

# it will navigate the user to there dashboards, look // username.html for this call
# i used url_for('ownedcourses', username=user.username)
@app.route('/users/<username>')
def ownedcourses(username):
    if username == current_user.username:
        return render_template('user_owned_courses.html', username=username)
    else:
        return redirect(url_for('users'))


# For admin user only
@app.route('/admin')
def admin():
    return render_template('admin_panel.html')

# locate the user to admin panel //locate admin_panel.html
@app.route('/admin/<action>', methods=['GET', 'POST'])
def actions(action):
    admin_panel = AdminPanel()

    if action == 'deleteuser':
        return render_template('adminpanel/deleteuser.html', action=action, admin_panel= admin_panel)
    if action == 'deleteitem':
        return render_template('adminpanel/deleteitem.html', action=action, admin_panel= admin_panel)
    
    if action == 'givetokens':
        form = AssignTokensForm()
        if request.method == 'POST':
            token_assin = AdminPanel()

            if form.validate_on_submit():
                # i got these value from inspect element of the form
                username = request.form.get('username')
                token_count = request.form.get('token_count')

                # assigning the token to the specific user
                token_assin.settokens(username, token_count)

                return redirect(url_for('admin'))
        
        return render_template('adminpanel/givetokens.html', action=action, admin_panel= admin_panel, form=form)


# value will be username and item names
@app.route('/admin/<action>/<value>')
def action_perform(action, value):
    if action == 'deleteuser':
        user = AdminPanel()
        
        # first we need to delete all the courses that user has posted
        # query will return a list and we will delete each item the user uploaded
        for item in Items.query.filter_by(uploader=value):
            user.deleteitem(item.name)    

        user.deleteuser(value)

        flash("Success! the user has been deleted", category='success')
        return redirect(url_for('admin'))
    
    if action == 'deleteitem':
        item = AdminPanel()
        item.deleteitem(value)

        flash("Success! the item has been deleted", category='success')
        return redirect(url_for('admin'))
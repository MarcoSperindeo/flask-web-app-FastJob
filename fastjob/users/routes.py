from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from fastjob import db, bcrypt
from fastjob.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, FeedbackForm
from fastjob.models import User, Post, Feedback, Comment, Booking
from flask_login import login_user, current_user, logout_user, login_required
from fastjob.users.utils import save_picture, save_cv, send_reset_email, send_email


users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        send_email(user.email, 'Subscription to FastJob', 'registration_email')
        flash('Check your email.', 'info')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if the user is already registered
        # if the user and the pw  match an instance of the db
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home')), flash('Login successful', 'success')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/delete_account/<int:user_id>")
@login_required
def delete_account(user_id):
    user = User.query.get_or_404(user_id)
    user_comments = Comment.query.filter_by(comment_author=user)
    user_feedbacks = Feedback.query.filter_by(feedback_author=user)
    for comment in user_comments:
        db.session.delete(comment)
    for feedback in user_feedbacks:
        db.session.delete(feedback)
    db.session.delete(current_user)
    db.session.commit()
    flash('Your account has been deleted! Thanks for having used our website.', 'success')
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.cv.data:
            cv_file = save_cv(form.cv.data)
            current_user.cv_file = cv_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.phone_num = form.phone_num.data
        current_user.paypal_link = form.paypal_link.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.user_posts', user_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
        if current_user.phone_num == '':
            form.phone_num.data = form.phone_num.default
        else:
            form.phone_num.data = current_user.phone_num
        form.paypal_link.data = current_user.paypal_link
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def user_posts(user_id):
    user = User.query.get_or_404(user_id)
    form = FeedbackForm()
    if form.validate_on_submit():
        rating = request.form.get('rate')
        feedback = Feedback(content=form.content.data, rating=rating, feedback_author=current_user, feedback_receiver=user)
        db.session.add(feedback)
        db.session.commit()
        flash('Your Feedback has been sent!', 'success')
        return redirect(url_for('users.user_posts', user_id=user.id))
    page_fb = request.args.get('page_fb', 1, type=int)
    page_post = request.args.get('page_post', 1, type=int)
    page_booking = request.args.get('page_bookings', 1, type=int)
    posts = Post.query.filter_by(post_author=user, available=True)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page_post, per_page=5)
    feedbacks_received = Feedback.query.filter_by(feedback_receiver=user)\
        .order_by(Feedback.timestamp.desc())\
        .paginate(page=page_fb, per_page=2)
    bookings = Booking.query.filter_by(booking_author=current_user)\
        .order_by(Booking.timestamp.desc())\
        .paginate(page=page_booking, per_page=2)

    return render_template('user_posts.html', title=user.username,
                           form=form, posts=posts, user=user, feedbacks=feedbacks_received, bookings=bookings)


@users.route("/user/ <int:user_id>/updatefeedback/<int:feedback_id>", methods=['GET', 'POST'])
@login_required
def update_feedback(user_id, feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(user_id)
    if feedback.feedback_author != current_user:
        abort(403)
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback.content = form.content.data
        feedback.rating = request.form.get('rate')
        db.session.commit()
        flash('Your Feedback has been updated!', 'success')
        return redirect(url_for('users.user_posts', user_id=user.id))
    elif request.method == 'GET':
        form.content.data = feedback.content
    return render_template ('moderator.html', title='Update Feedback', form=form, feedback=feedback, legend='Update Feedback')



@users.route("/user/<int:user_id>/deletefeedback/<int:feedback_id>", methods=['GET','POST'])
@login_required
def delete_feedback(user_id, feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user = Feedback.query.get_or_404(user_id)
    if feedback.feedback_author != current_user:
        abort(403)
    db.session.delete(feedback)
    db.session.commit()
    flash('Your feedback has been deleted! Other users will no longer see it.', 'danger')
    return redirect(url_for('users.user_posts', user_id=user.id))


@users.route("/moderator/")
@login_required
def moderator():
    current_user.moderator = False
    db.session.commit()
    return render_template('moderator.html')


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is False:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

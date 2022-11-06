import os
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message
from fastjob import mail
from fastjob.models import User

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # The PIL library has a functions that allows to automatically
    # resize the picture that has been uploaded
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # form_picture.save(picture_path)
    i.save(picture_path)

    return picture_fn


def save_cv(form_cv):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_cv.filename)
    cv_fn = random_hex + f_ext
    cv_path = os.path.join(current_app.root_path, 'static/profile_cvs', cv_fn)
    form_cv.save(cv_path)

    return cv_fn


def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    user = User.query.filter_by(email=to).first()
    msg.html = render_template(template + '.html', user=user, **kwargs)
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    token_url = url_for('users.reset_token', token=token, _external=True)
    msg.body = 'To reset your password, visit the following link: {}'.format(token_url)
    mail.send(msg)  # If you did not make this request then simply ignore this email and no changes will be made.
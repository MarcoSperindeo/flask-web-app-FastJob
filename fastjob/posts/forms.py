from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Regexp, Length


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()],
                       choices=[('offer', 'Job Offer'), ('application', 'Job Application')])
    sector = SelectField('Sector', validators=[DataRequired()],
                         choices=[('Animal Care', 'Animal Care'), ('Beauty Care and Wellness', 'Beauty Care and Wellness'),
                                  ('Computer and Web', 'Computer and Web'),
                                  ('Consultancy and Professional Services',
                                   'Consultancy and Professional Services'),
                                  ('Courses and Classes', 'Courses and Classes'),
                                  ('Events', 'Events'), ('Gardening', 'Gardening'),
                                  ('House Maintenance', 'House Maintenance'),
                                  ('Photography', 'Photography'),
                                  ('Services for Businesses', 'Services for Businesses'),
                                  ('Sports and Fitness', 'Sports and Fitness'),
                                  ('Transport and Delivery', 'Transport and Delivery'),
                                  ('Private Tuition and Lectures', 'Private Tuition and Lectures'),
                                  ('Others', 'Others')])
    price = StringField('Fee', validators=[DataRequired(), Regexp('^(?!$)(?!0+$)\d{0,8}(?:\.\d{1,2})?$',
                                                                  message="Price must be in the format XXX.XX")])
    datejob = DateField(description='Time in which the event will occur')
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address', validators=[Length(min=0, max=100)])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    min_price = StringField('Min. Fee', validators=[Regexp('^(?!0+$)\d{0,8}(?:\.\d{1,2})?$',
                                                                            message="Price must be in the format XXX.XX")])
    max_price = StringField('Max. Fee', validators=[Regexp('^(?!0+$)\d{0,8}(?:\.\d{1,2})?$',
                                                                            message="Price must be in the format XXX.XX")])
    start_datejob = DateField('Start date')
    end_datejob = DateField('End date')
    sector = SelectField('Sector', validators=[DataRequired()],
                         choices=[('Animal Care', 'Animal Care'),
                                  ('Beauty Care and Wellness', 'Beauty Care and Wellness'),
                                  ('Computer and Web', 'Computer and Web'),
                                  ('Consultancy and Professional Services',
                                   'Consultancy and Professional Services'),
                                  ('Courses and Classes', 'Courses and Classes'),
                                  ('Events', 'Events'), ('Gardening', 'Gardening'),
                                  ('House Maintenance', 'House Maintenance'),
                                  ('Photography', 'Photography'),
                                  ('Services for Businesses', 'Services for Businesses'),
                                  ('Sports and Fitness', 'Sports and Fitness'),
                                  ('Transport and Delivery', 'Transport and Delivery'),
                                  ('Private Tuition and Lectures', 'Private Tuition and Lectures'),
                                  ('Others', 'Others')])
    city = StringField('City', validators=[Length(min=0, max=20)])
    submit = SubmitField('Search')

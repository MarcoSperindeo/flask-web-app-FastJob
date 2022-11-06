# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime as dt
import datetime
import jwt
from flask import current_app
from fastjob import db, login_Manager
from flask_login import UserMixin


@login_Manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    about_me = db.Column(db.Text, nullable=True)
    phone_num = db.Column(db.String(20), nullable=True)
    paypal_link = db.Column(db.String(40), nullable=True)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    cv_file = db.Column(db.String(120), nullable=True)
    moderator = db.Column(db.Boolean, nullable=False, default=False)

    user_posts = db.relationship("Post", back_populates="post_author")
    user_bookings = db.relationship("Booking", back_populates="booking_author")
    user_comments = db.relationship('Comment', back_populates="comment_author")
    feedbacks_posted = db.relationship('Feedback', back_populates="feedback_author")
    feedbacks_received = db.relationship('Feedback', back_populates="feedback_receiver")

    """  
    # DEPRECATED since v2.00 of 'itsdangerous' package  
    def get_reset_token(self, expires_sec=1800):
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
        """

    def get_reset_token(self, expiration=1800):
        reset_token = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                       + datetime.timedelta(seconds=expiration)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token

    @staticmethod
    def verify_reset_token(self, token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return "User('{self.id}', '{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    date_job = db.Column(db.Date, nullable=False, default=dt.utcnow)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    sector = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float(12), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False, default='')
    available = db.Column(db.Boolean, nullable=True, default=True)

    post_author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    post_author = db.relationship("User", back_populates="user_posts")
    post_bookings = db.relationship("Booking", back_populates="booking_post")
    post_comments = db.relationship('Comment', back_populates="comment_post")

    def __repr__(self):
        return "Post('{self.id}', '{self.title}', '{self.content}')"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    rating = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)

    booking_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    booking_author = db.relationship("User", back_populates="user_bookings")
    booking_post = db.relationship("Post", back_populates="post_bookings")

    def __repr__(self):
        return "Booking('{self.id}', '{self.timestamp}', '{self.rating}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    disabled = db.Column(db.Boolean)

    comment_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    comment_author = db.relationship("User", back_populates="user_comments")
    comment_post = db.relationship("Post", back_populates="post_comments")

    def __repr__(self):
        return "Comment('{self.id}', '{self.content}')"


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    rating = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=dt.utcnow)
    feedback_author_id = db.Column(db.Integer)
    feedback_receiver_id = db.Column(db.Integer)
    __table_args__ = (
        db.ForeignKeyConstraint(
            [feedback_author_id, feedback_receiver_id],
            ['user.id', 'user.id'],
        ),
    )

    feedback_author = db.relationship("User", back_populates="feedbacks_posted", foreign_keys=[feedback_author_id])
    feedback_receiver = db.relationship("User", back_populates="feedbacks_received", foreign_keys=[feedback_receiver_id])

    def __repr__(self):
        return "Feedback('{self.id}', '{self.content}', '{self.rating}')"

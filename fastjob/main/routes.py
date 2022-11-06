from flask import render_template, request, Blueprint
from fastjob.models import Post


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(available=True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Home', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')






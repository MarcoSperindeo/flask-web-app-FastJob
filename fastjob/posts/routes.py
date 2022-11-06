from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from fastjob import db
from fastjob.posts.forms import PostForm, CommentForm, SearchForm
from fastjob.models import Post, Comment, Booking
from sqlalchemy import and_
from datetime import datetime


posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.moderator:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, type=form.type.data, sector=form.sector.data,
                    price=float(form.price.data), date_job=form.datejob.data, city=form.city.data,
                    address=form.address.data, post_author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    form.datejob.data = datetime.utcnow()
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data,
                          comment_post=post,
                          comment_author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    booking = Booking.query.filter_by(booking_author=current_user, booking_post=post).first()
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(comment_post=post).order_by(Comment.timestamp.asc()).paginate(page=page, per_page=5)
    return render_template('post.html', title=post.title, post=post, form=form,
                           comments=comments, booking=booking, legend='New Comment')


@posts.route("/post/<int:post_id>/updatepost", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.post_author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.type = form.type.data
        post.sector = form.sector.data
        post.title = form.title.data
        post.content = form.content.data
        post.city = form.city.data
        post.address = form.address.data
        post.date_job = form.datejob.data
        post.price = float(form.price.data)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.type.data = post.type
        form.sector.data = post.sector
        form.title.data = post.title
        form.content.data = post.content
        form.city.data = post.city
        form.address.data = post.address
        form.datejob.data = post.date_job
        form.price.data = post.price
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/deletepost", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.post_author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted! Other users will no longer be able to see your post.', 'danger')
    return redirect(url_for('main.home'))


@posts.route('/post/<int:post_id>/book', methods=['GET', 'POST'])
@login_required
def book(post_id):
    print(post_id)
    post = Post.query.get_or_404(post_id)
    if current_user == post.post_author:
        abort(403)
    booking = Booking(booking_author=current_user, booking_post=post, rating=0)
    post.available = False
    db.session.add(booking)
    db.session.commit()
    flash('Job booked successfully!', 'success')
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route('/post/<int:post_id>/unbook/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def unbook(post_id, booking_id):
    print(booking_id)
    post = Post.query.get_or_404(post_id)
    booking = Booking.query.get_or_404(booking_id)
    if current_user == post.post_author:
        abort(403)
    if current_user != booking.booking_author:
        abort(403)
    db.session.delete(booking)
    post.available = True
    db.session.commit()
    flash('Job unbooked!', 'success')
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route("/post/<int:post_id>/updatecomment/<int:comment_id>", methods=['GET', 'POST'])
@login_required
def update_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(post_id)
    if comment.comment_author != current_user:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Your comment has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.content.data = comment.content
    # page = request.args.get('page', 1, type=int)
    # comments = Comment.query.filter_by(post=post).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=5)
    # return render_template('post.html',title=post.title,post=post,form=form,comments=comments,legend='New Comment')
    # or alternatively we can render a different template comment.html
    # where comment.html is a page extending the layout and showing only the comments form
    return render_template('comment.html', title='Update Comment', form=form, comment=comment, legend='Update Comment')


@posts.route("/post/<int:post_id>/deletecomment/<int:comment_id>", methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(post_id)
    if comment.comment_author != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted! Other users will no longer see your comment.', 'danger')
    return redirect(url_for('posts.post', post_id=post.id))


@posts.route("/offers", methods=['GET', 'POST'])
@login_required
def offers():
    form = SearchForm()
    if form.validate_on_submit():
        min_price = form.min_price.data
        max_price = form.max_price.data
        start_date = form.start_datejob.data
        end_date = form.end_datejob.data
        sector = form.sector.data
        city = form.city.data
        if city == '':
            if min_price != '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price), Post.price <= float(max_price)))\
                    .filter_by(type='offer', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price == '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter_by(type='offer', sector=sector)\
                    .paginate(page=page, per_page=5)
            elif min_price != '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price)))\
                    .filter_by(type='offer', sector=sector, available=True)\
                    .paginate(page=page,per_page=5)
            elif min_price == '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price <= float(max_price)))\
                    .filter_by(type='offer', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
        else:
            if min_price == '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter_by(type='offer', sector=sector, city=city, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price != '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price)))\
                    .filter_by(type='offer', city=city, sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price == '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price <= float(max_price)))\
                    .filter_by(type='offer', city=city, sector=sector, available=True)\
                    .paginate(page=page, per_page=5)

            elif min_price != '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price), Post.price <= float(max_price)))\
                    .filter_by(type='offer', sector=sector, city=city, available=True)\
                    .paginate(page=page, per_page=5)
        return render_template('posts_offers.html', title='Job Offers', posts=posts, form=form)

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(type='offer', available=True).paginate(page=page, per_page=5)
    form.start_datejob.data = datetime.utcnow()
    form.end_datejob.data = datetime.utcnow()
    return render_template('posts_offers.html', title='Job Offers', posts=posts, form=form)


@posts.route("/applications", methods=['GET', 'POST'])
@login_required
def applications():
    form = SearchForm()
    if form.validate_on_submit():
        min_price = form.min_price.data
        max_price = form.max_price.data
        start_date = form.start_datejob.data
        end_date = form.end_datejob.data
        sector = form.sector.data
        city = form.city.data
        if city == '':
            if min_price != '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price), Post.price <= float(max_price)))\
                    .filter_by(type='application', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price == '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter_by(type='application', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price != '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price)))\
                    .filter_by(type='application', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price == '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price <= float(max_price)))\
                    .filter_by(type='application', sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
        else:
            if min_price == '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter_by(type='application', sector=sector, city=city, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price != '' and max_price == '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price)))\
                    .filter_by(type='application', city=city, sector=sector, available=True)\
                    .paginate(page=page, per_page=5)
            elif min_price == '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price <= float(max_price)))\
                    .filter_by(type='application', city=city, sector=sector, available=True)\
                    .paginate(page=page,per_page=5)
            elif min_price != '' and max_price != '':
                page = request.args.get('page', 1, type=int)
                posts = Post.query.filter(and_(Post.date_job >= start_date, Post.date_job <= end_date))\
                    .filter(and_(Post.price >= float(min_price), Post.price <= float(max_price)))\
                    .filter_by(type='application', sector=sector, city=city, available=True)\
                    .paginate(page=page, per_page=5)
        return render_template('posts_applications.html', title='Job Applications', posts=posts, form=form)

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(type='application', available=True).paginate(page=page, per_page=5)
    form.start_datejob.data = datetime.utcnow()
    form.end_datejob.data = datetime.utcnow()
    return render_template('posts_applications.html', title='Job Applications', posts=posts, form=form)






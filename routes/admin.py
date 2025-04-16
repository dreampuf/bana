#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Admin routes for Bana
# Author: dreampuf (original), updated by Codegen

from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify, session, flash
from google.cloud import ndb
from functools import wraps
from models.post import Post, PostStatus
from models.category import Category
from models.comment import Comment
from models.user import User
from config import config

admin_routes = Blueprint('admin', __name__)

# Admin authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'curr_ukey' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_routes.route('/login/', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.check(email, password)
        if user:
            session['curr_ukey'] = email
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid email or password')
    
    return render_template('AdminLogin.html', config=config)

@admin_routes.route('/logout/')
def logout():
    """Admin logout"""
    session.pop('curr_ukey', None)
    return redirect(url_for('admin.login'))

@admin_routes.route('/')
@login_required
def index():
    """Admin dashboard"""
    return render_template('AdminIndex.html', config=config)

@admin_routes.route('/post/')
@login_required
def posts():
    """Post management page"""
    page = request.args.get('page', 1, type=int)
    posts_per_page = config.POST_PAGE_COUNT
    
    # Query posts
    query = Post.query().order(-Post.date_created)
    posts = query.fetch(posts_per_page, offset=(page-1)*posts_per_page)
    
    # Get total count for pagination
    total_posts = query.count()
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page
    
    return render_template('AdminPost.html',
                          posts=posts,
                          page=page,
                          total_pages=total_pages,
                          config=config)

@admin_routes.route('/post/new/', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create new post"""
    if request.method == 'POST':
        title = request.form.get('title')
        category_keyname = request.form.get('category')
        url = request.form.get('url')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        format = request.form.get('format', 'html')
        status = int(request.form.get('status', PostStatus.NORMAL))
        enablecomment = bool(request.form.get('enablecomment', True))
        
        # Validate required fields
        if not title or not category_keyname or not url or not content:
            flash('Missing required fields')
            return redirect(url_for('admin.new_post'))
        
        # Create post
        Post.new(
            title=title,
            category_keyname=category_keyname,
            author_keyname=session['curr_ukey'],
            url=url,
            keyword=[],
            tags=tags,
            content=content,
            status=status,
            format=format,
            enablecomment=enablecomment
        )
        
        flash('Post created successfully')
        return redirect(url_for('admin.posts'))
    
    # Get categories for dropdown
    categories = Category.query().order(Category.order).fetch()
    
    return render_template('AdminPost_single.html',
                          categories=categories,
                          config=config)

@admin_routes.route('/post/<int:post_id>/', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit existing post"""
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)
    
    if request.method == 'POST':
        title = request.form.get('title')
        category_keyname = request.form.get('category')
        url = request.form.get('url')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        format = request.form.get('format', 'html')
        status = int(request.form.get('status', PostStatus.NORMAL))
        enablecomment = bool(request.form.get('enablecomment', True))
        
        # Validate required fields
        if not title or not category_keyname or not url or not content:
            flash('Missing required fields')
            return redirect(url_for('admin.edit_post', post_id=post_id))
        
        # Update post
        Post.modify(
            post_id=post_id,
            title=title,
            category_keyname=category_keyname,
            author_keyname=session['curr_ukey'],
            url=url,
            keyword=[],
            tags=tags,
            content=content,
            status=status,
            format=format,
            enablecomment=enablecomment
        )
        
        flash('Post updated successfully')
        return redirect(url_for('admin.posts'))
    
    # Get categories for dropdown
    categories = Category.query().order(Category.order).fetch()
    
    return render_template('AdminPost_single.html',
                          post=post,
                          categories=categories,
                          config=config)

@admin_routes.route('/category/', methods=['GET', 'POST'])
@login_required
def categories():
    """Category management page"""
    if request.method == 'POST':
        url = request.form.get('url')
        title = request.form.get('title')
        description = request.form.get('description', '')
        order = int(request.form.get('order', 0))
        
        # Validate required fields
        if not url or not title:
            flash('Missing required fields')
            return redirect(url_for('admin.categories'))
        
        # Create category
        Category.new(
            url=url,
            title=title,
            description=description,
            order=order
        )
        
        flash('Category created successfully')
        return redirect(url_for('admin.categories'))
    
    # Get categories
    categories = Category.query().order(Category.order).fetch()
    
    return render_template('AdminCategory.html',
                          categories=categories,
                          config=config)

@admin_routes.route('/config/', methods=['GET', 'POST'])
@login_required
def site_config():
    """Site configuration page"""
    if request.method == 'POST':
        # Update configuration settings
        for key, value in request.form.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        flash('Configuration updated successfully')
        return redirect(url_for('admin.site_config'))
    
    return render_template('AdminConfig.html', config=config)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Blog routes for Bana
# Author: dreampuf (original), updated by Codegen

from flask import Blueprint, request, render_template, redirect, url_for, abort, jsonify
from google.cloud import ndb
from models.post import Post
from models.category import Category
from models.comment import Comment
from config import config

blog_routes = Blueprint('blog', __name__)

@blog_routes.route('/')
def index():
    """Main blog index page"""
    page = request.args.get('page', 1, type=int)
    posts_per_page = config.INDEX_POST_COUNT
    
    # Query posts
    query = Post.query().filter(Post.status == 0).order(-Post.date_created)
    posts = query.fetch(posts_per_page, offset=(page-1)*posts_per_page)
    
    # Get total count for pagination
    total_posts = query.count()
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page
    
    return render_template('index.html', 
                          posts=posts,
                          page=page,
                          total_pages=total_pages,
                          config=config)

@blog_routes.route('/category/<category_key_name>/')
def category(category_key_name):
    """Category view page"""
    page = request.args.get('page', 1, type=int)
    posts_per_page = config.INDEX_POST_COUNT
    
    # Get category
    category = Category.get_by_id(category_key_name)
    if not category:
        abort(404)
    
    # Query posts in this category
    query = Post.query().filter(Post.category == category.key).order(-Post.date_created)
    posts = query.fetch(posts_per_page, offset=(page-1)*posts_per_page)
    
    # Get total count for pagination
    total_posts = query.count()
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page
    
    return render_template('category.html',
                          category=category,
                          posts=posts,
                          page=page,
                          total_pages=total_pages,
                          config=config)

@blog_routes.route('/comment/<int:post_id>/', methods=['POST'])
def comment(post_id):
    """Handle comment submission"""
    post = Post.get_by_id(post_id)
    if not post:
        abort(404)
    
    if not post.enablecomment:
        abort(403)
    
    # Get comment data
    nickname = request.form.get('nickname')
    email = request.form.get('email')
    website = request.form.get('website')
    content = request.form.get('content')
    
    # Validate required fields
    if not nickname or not email or not content:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    # Create comment
    comment = Comment(
        parent=post.key,
        belong=post.key,
        nickname=nickname,
        email=email,
        website=website,
        content=content,
        ip=request.remote_addr
    )
    comment.put()
    
    return redirect(url_for('blog.view', path=post.url))

@blog_routes.route('/<path:path>')
def view(path):
    """View a single post"""
    post = Post.query().filter(Post.url == path).get()
    if not post:
        abort(404)
    
    # Increment view count
    post.views += 1
    post.put()
    
    # Get comments
    comments = Comment.query(ancestor=post.key).order(Comment.date_created).fetch()
    
    return render_template('single.html',
                          post=post,
                          comments=comments,
                          config=config)

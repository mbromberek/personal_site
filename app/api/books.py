# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
import sys
import os

# Third party classes
import feedparser
import requests
from flask import jsonify, request, url_for, abort, current_app

# Customer classes
from app import logger
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.model.book import Book

@bp.route('/books/refresh/', methods=['GET'])
@token_auth.login_required
def refresh_book_status():
    logger.info('refresh_book_status')
    usr_id = token_auth.current_user().id
    books, status = refresh_books(usr_id)
    logger.debug(books)
    return jsonify(books), status

def refresh_books(usr_id):
    # If not original user do not perform refresh
    if usr_id != 1:
        return[]
    
    current_reading = current_app.config['CURR_READ_RSS']
    read_feed = current_app.config['READ_RSS']
    curr_reading_val = 'reading'
    read_val = 'read'

    books = []

    try:
        logger.debug('START: Get Current Reading Books')
        # Get Books Currently being read on GoodReads
        Feed = feedparser.parse(current_reading)
        if Feed.status != 200:
            logger.error(Feed.status)
            return [], Feed.status
        gr_current_books = Feed.entries
        logger.debug('END: Get Current Reading Books')

        # Get 2 most recently read books
        logger.debug('START: Get Read Books')
        Feed = feedparser.parse(read_feed)
        if Feed.status != 200:
            logger.error(Feed.status)
            return [], Feed.status
        read_books = Feed.entries
        logger.debug('END: Get Read Books')
    except:
        return [], 400


    # Convert from GR JSON feed format to Book Dictionary format
    gr_book_lst = []
    for gr_book in gr_current_books:
        gr_book_lst.append(Book.GR_to_dict(gr_book, usr_id, curr_reading_val))

    gr_book_lst.append(Book.GR_to_dict(read_books[0], usr_id, read_val))
    gr_book_lst.append(Book.GR_to_dict(read_books[1], usr_id, read_val))

    # Get Books from DB
    query = Book.query.filter_by(user_id=usr_id)
    db_books = query.all()

    # Loop through books in DB, and delete any not in gr_book_lst
    # Keep track of GR books that are not already in DB
    for db_book in db_books:
        match = False
        for gr_book in gr_book_lst:
            if db_book.compare_goodreads(gr_book):
                match = True
                gr_book['already_exist'] = True
                break
        if not match:
            # Remove book from DB
            if os.path.exists('./app/'+db_book.cover_img_locl_path):
                os.remove('./app/'+db_book.cover_img_locl_path)
            db.session.delete(db_book)
            db.session.commit()
        else:
            books.append(db_book.to_dict())

    # Insert GR books that are not already in DB
    for gr_book in gr_book_lst:
        if gr_book['already_exist'] == False:
            # Download book cover in medium and large sizes
            img_data = requests.get(gr_book['img_url']).content
            book_img_title = gr_book['title'] + '_' + gr_book['author'] + '_' + gr_book['status'] + '.jpg'
            book_img_title = book_img_title.replace(' ','_').replace('#','').replace(':','').replace('<','').replace('>','')
            with open('./app/static/images/books/' + book_img_title, 'wb') as handler:
                handler.write(img_data)
            book = Book.from_dict(gr_book)
            book.cover_img_locl_path = 'static/images/books/' + book_img_title
            db.session.add(book)
            db.session.commit()
            books.append(book.to_dict())

    return books, 200

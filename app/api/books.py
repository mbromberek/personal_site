# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime
import sys

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
            db.session.delete(db_book)
            db.session.commit()
        else:
            books.append(db_book.to_dict())

    # Insert GR books that are not already in DB
    for gr_book in gr_book_lst:
        if gr_book['already_exist'] == False:
            book = Book.from_dict(gr_book)
            db.session.add(book)
            db.session.commit()
            books.append(book.to_dict())

    return books, 200
        

    # loop through list of GR current books and add any books not in remaining list of current books from database
    print('Currently Reading:')
    for gr_book in gr_books:
        book_dict = {'status':'reading','title':gr_book['title'], 'author':gr_book['author_name'], 'strt_reading_dt':gr_book['user_date_added']}
        # Does book with same title, author, start date already exist?
        # If yes do nothing
        # If no then insert

        logger.info ('Title: ' + gr_book['title'])
        logger.info ('Author: ' + gr_book['author_name'])
        logger.info ('Image URL: ' + gr_book['book_medium_image_url'] + '\n')
        logger.info ('Summary: ' + gr_book['summary'])
        logger.info ('Started: ' + gr_book['user_date_added'])
        # Download book cover in medium and large sizes
        # img_data_medium = requests.get(book['book_medium_image_url']).content
        # img_data_large = requests.get(book['book_large_image_url']).content
        # with open('book_img_large.jpg', 'wb') as handler:
        #     handler.write(img_data_large)
        # with open('book_img_medium.jpg', 'wb') as handler:
        #     handler.write(img_data_medium)
        books.append({'status':'reading','title':book['title'], 'author':book['author_name'], 'strt_reading_dt':book['user_date_added']})

    # Get 2 most recently read books
    Feed = feedparser.parse(read_feed)
    read_books = Feed.entries
    last_book_1 = read_books[0]
    logger.info ('\nLast 2 books:')
    logger.info('Title: ' + last_book_1['title'])
    logger.info('Author: ' + last_book_1['author_name'])
    logger.info('Image medium URL: ' + last_book_1['book_medium_image_url'])
    logger.info('Image URL: ' + last_book_1['book_small_image_url'])
    # print ('Summary: ' + last_book_1['summary'])
    logger.info ('Finished on: ' + last_book_1['user_read_at'])
    books.append({'status':'finished','title':last_book_1['title'], 'author':last_book_1['author_name'], 'finished_reading_dt':last_book_1['user_read_at']})


    last_book_2 = read_books[1]
    logger.info('Title: ' + last_book_2['title'])
    logger.info('Author: ' + last_book_2['author_name'])
    logger.info('Image URL: ' + last_book_2['book_small_image_url'])
    # print ('Summary: ' + last_book_2['summary'])
    logger.info ('Finished on: ' + last_book_2['user_read_at'])
    books.append({'status':'finished','title':last_book_2['title'], 'author':last_book_2['author_name'], 'finished_reading_dt':last_book_2['user_read_at']})

    return books
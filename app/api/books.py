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
    books = refresh_books(usr_id)
    return jsonify(books), 200

def refresh_books(usr_id):
    # If not original user do not perform refresh
    if usr_id != 1:
        return[]
    
    current_reading = current_app.config['CURR_READ_RSS']
    read_feed = current_app.config['READ_RSS']

    books = []

    # Get Books Currently being read
    Feed = feedparser.parse(current_reading)
    current_book_lst = Feed.entries
    print('Currently Reading:')
    for book in current_book_lst:
        # print(book)
        logger.info ('Title: ' + book['title'])
        logger.info ('Author: ' + book['author_name'])
        logger.info ('Image URL: ' + book['book_medium_image_url'] + '\n')
        logger.info ('Summary: ' + book['summary'])
        logger.info ('Started: ' + book['user_date_added'])
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
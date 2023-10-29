# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2021, Mike Bromberek
All rights reserved.
'''

# First party classes
from datetime import datetime

# Customer classes
from app import logger
from app import db

dt_str_format = '%Y-%m-%d'
gr_datetime_format = '%a, %d %b %Y %H:%M:%S %z'
CURR_READING_VAL = 'reading'
READ_VAL = 'read'


class Book(db.Model):
    __table_args__ = {"schema": "media", 'comment':'Store current and previous read books'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fitness.user.id'))
    status = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(500), nullable=True)
    cover_img_locl_path = db.Column(db.Text(), nullable=True)
    strt_reading_dt = db.Column(db.DateTime, nullable=True)
    finished_reading_dt = db.Column(db.DateTime, nullable=True)
    isrt_ts = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Book: {}, status: {}>'.format( self.title, self.status)

    def __lt__(self, other):
        if self.finished_reading_dt is not None and other.finished_reading_dt is not None:
            return ((self.finished_reading_dt < other.finished_reading_dt))
        else:
            return ((self.strt_reading_dt < other.strt_reading_dt))

    def __gt__(self, other):
        if self.finished_reading_dt is not None:
            return ((self.finished_reading_dt > other.finished_reading_dt))
        else:
            return ((self.strt_reading_dt > other.strt_reading_dt))

    def compare_goodreads(self, gr_book):
        if self.title == gr_book['title'] \
            and self.author == gr_book['author'] \
            and self.strt_reading_dt == gr_book['strt_reading_dt'] \
            and self.finished_reading_dt == gr_book['finished_reading_dt'] \
            and self.status == gr_book['status']:
            return True
        else:
            return False
    @staticmethod
    def GR_to_dict(gr_book, usr_id, status):
        book_dict = {'status':status, 'user_id':usr_id, 'cover_img_locl_path':''}
        if status == 'reading':
            book_dict['img_url'] = gr_book['book_medium_image_url']
        else:
            book_dict['img_url'] = gr_book['book_small_image_url']
        if gr_book['user_date_added'] is not None and gr_book['user_date_added'] != '':
            book_dict['strt_reading_dt'] = \
                datetime.strptime(gr_book['user_date_added'],gr_datetime_format).date()
        else:
            book_dict['strt_reading_dt'] = None

        if 'title' in gr_book and len(gr_book['title']) <500:
            book_dict['title'] = gr_book['title']
        if 'author_name' in gr_book and len(gr_book['author_name']) <500:
            book_dict['author'] = gr_book['author_name']
        if gr_book['user_read_at'] is not None and gr_book['user_read_at'] != '':
            book_dict['finished_reading_dt'] = \
                datetime.strptime(gr_book['user_read_at'],gr_datetime_format).date()
        else:
            book_dict['finished_reading_dt'] = None
        book_dict['already_exist'] = False
        return book_dict
    
    def to_dict(self):
        book_dict = {'status':self.status,
            'title':self.title, 
            'author':self.author, 
            'user_id':self.user_id
        }
        if self.strt_reading_dt is not None:
            book_dict['strt_reading_dt'] = self.strt_reading_dt.strftime(dt_str_format)
        else:
            book_dict['strt_reading_dt'] = ''
        if self.finished_reading_dt is not None:
            book_dict['finished_reading_dt'] = self.finished_reading_dt.strftime(dt_str_format)
        else:
            book_dict['finished_reading_dt'] = ''

        if self.cover_img_locl_path == '':
            book_dict['cover_img'] = 'N'
        else:
            book_dict['cover_img'] = 'Y'
        return book_dict


    @staticmethod
    def from_dict(book_dict):
        book = Book()
        book.user_id = book_dict['user_id']
        book.status = book_dict['status']
        book.title = book_dict['title']
        book.author = book_dict['author']
        book.cover_img_locl_path = book_dict['cover_img_locl_path']
        book.strt_reading_dt = book_dict['strt_reading_dt']
        book.finished_reading_dt = book_dict['finished_reading_dt']

        return book
from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import users, errors, tokens, workouts, workout_intervals, books, goals

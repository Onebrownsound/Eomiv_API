from collections import defaultdict
import os
import operator
import datetime

from flask import Flask, jsonify, request

from database import db_session as db
from models import User, Transaction

app = Flask(__name__)


def register(id=None, timestamp=None, country=None, ip=None):
    """
     Create a new user in DB.
    """

    user = User(id=int(id),
                timestamp=timestamp,
                country=country,
                ip=ip)

    db.merge(user)  # Adds record, else if record exists update with new data accordingly.
    db.commit()


def transaction(action_type=None, user_id=None, timestamp=None, video_id=None):
    """
    Does all other DB transactions LIKE,WATCH,UPLOAD
    """

    user_id = int(user_id)
    video_id = int(video_id)
    trans = Transaction(action_type=action_type,
                        owner=user_id,
                        timestamp=timestamp,
                        video_id=video_id)
    db.add(trans)
    db.commit()


def process_data():
    """
    Open file->read lines-> dump into DB
    Divided operations into two camps Register and Tranaction.
    Registering adds an entry to User table.
    Transactions add an entry to the Transaction table.
    """

    # Open data file. Split by newline and iterate over each. Parse operators into two DB tables.
    with open(os.path.join(os.getcwd(), 'data.dump'))as f:
        content = f.read().split('\n')
        for line in content:

            # swingfield takes a dual roll for REGISTER operations it is the country and for all others
            # it assumes the role of video_id.
            split = line.split(' ')
            split_length = len(split)
            if split_length == 5:
                time_stamp, action_type, user_id, swing_field, ip = split
            elif split_length == 4:
                time_stamp, action_type, user_id, swing_field = split

            if action_type == 'REGISTER':
                register(id=user_id,
                         timestamp=time_stamp,
                         country=swing_field,
                         ip=ip)
            elif action_type in ['UPLOAD', 'WATCH', 'LIKE']:
                transaction(action_type=action_type,
                            user_id=user_id,
                            timestamp=time_stamp,
                            video_id=swing_field)
            else:
                raise TypeError  # Or some error which specifies an invalid OPERATOR has been found


@app.route('/user/<int:user_id>')
def get_user_info(user_id=None):
    """
    API end-point for the user. Requires <user_id> parameter. Supports GET POST PATCH and DELETE
    """
    if request.method == 'GET':
        user = User.query.filter_by(id=user_id).first()  # Look up User from DB if not return a 404

        # Below are Select * Statements with appropriate WHERE clauses
        uploaded_videos = Transaction.query.filter_by(owner=user.id, action_type='UPLOAD').all()
        watched_videos = Transaction.query.filter_by(owner=user.id, action_type='WATCH').all()
        liked_videos = Transaction.query.filter_by(owner=user.id, action_type='LIKE').all()
        return jsonify({'user_id': user_id,
                        'uploaded_videos': [video.video_id for video in uploaded_videos],
                        'watched_videos': [video.video_id for video in watched_videos],
                        'liked_videos': [video.video_id for video in liked_videos]})

    elif request.method == 'POST':  # Create new user
        register(id=user_id,
                 timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 country=request.args.get('country'),
                 ip=request.args.get('ip'))


    elif request.method == 'PATCH':
        # ATM these are the only columns I believe should be mutable in the USER table.
        new_country = request.args.get('country')
        new_ip = request.args.get('ip')
        User.query.filter_by(id=user_id).update({"country": new_country, "ip": new_ip})
        return jsonify({'status': 'OK', 'user_id': user_id, 'operation': 'UPDATE/PATCH'})

    elif request.method == 'DELETE':
        user = User.query.filter(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'OK', 'user_id': user_id, 'operation': 'DELETE'})


@app.route('/video/<int:video_id>', methods=['GET'])
def video_by_country(video_id=None):
    """
     This method fetches all video watch transactions from the DB. Then for each video does a reverse lookup on that
     particular video owner's country
    """
    video_id = int(video_id)
    videos_by_country_count = defaultdict(int)
    video_candidates = Transaction.query.filter_by(action_type='WATCH', video_id=video_id)
    for video in video_candidates:
        user = User.query.filter_by(id=video.owner).first()
        videos_by_country_count[user.country] += 1
    return jsonify(videos_by_country_count)


@app.route('/country/<string:country_name>', methods=['GET'])
def get_users_by_country(country_name=None):
    """
    Only Accepts GET method. Input is a country name. Outputs list of users from said country.
    """
    user_list = User.query.filter_by(country=country_name).all()
    user_list = [user.id for user in user_list]
    return jsonify({'country_name': country_name,
                    'user_ids': user_list})


@app.route('/trending', methods=['GET'])
def top_five_videos():
    """
    This endpoint calculates and returns the top 5 most watched videos.
    This is not good. Probably should have a real time mechanic which adds/counts video views over a particular time
    slice maintaining the top 5 in real time. Much more efficient than what is below
    O(M + NLOG(N) where M is the DB query cost and N is the size of video_frequency dictionary"""
    video_frequency = defaultdict(int)
    watched_videos = Transaction.query.filter_by(action_type='WATCH')
    for video in watched_videos:
        video_frequency[video.video_id] += 1
    top_five = sorted(video_frequency.items(), key=operator.itemgetter(1), reverse=True)[:5]
    top_five = [{'video_id': video[0], 'watched': video[1]} for video in top_five]
    return jsonify(top_five)


if __name__ == '__main__':
    app.run()

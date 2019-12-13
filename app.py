from flask import Flask, request
import dber

app = Flask(__name__)


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/receiver', methods=['POST', 'GET'])
def yeet():
    return "no."


@app.route('/bestN', methods=['GET'])
def best_n():
    return "no."


@app.route('/createUser/<uid>', methods=['POST'])
def create_user(uid):
    # TODO: implement
    # for testing: 1-10 return False (already taken), 10+ print to console
    return True


@app.route('/getrecommendations/<uid>', methods=['GET'])
def get_recommendations(uid):
    uid = int(uid)
    resp = dber.recommend_books(uid, num_recommendations=25)
    return resp


@app.route('/gethistory/<uid>', methods=['GET'])
def ratings_history(uid):
    uid = int(uid)
    resp = dber.user_rating_history(uid)
    return resp


@app.route('/search/<uid>/<pattern>', methods=['GET'])
def search_books(uid, pattern):
    uid = int(uid)
    resp = dber.pattern_matches(uid, pattern, num_matches=25)
    return resp


@app.route('/rate/<uid>/<book_id>/<rating>', methods=['POST'])
def add_rating(uid, book_id, rating):
    dber.add_rating(int(uid), int(book_id), int(rating))
    return "accepted"


@app.route('/delete/<uid>/<book_id>/', methods=['POST'])
def del_rating(uid, book_id):
    dber.remove_rating(int(uid), int(book_id))
    return "accepted"


if __name__ == '__main__':
    app.run()

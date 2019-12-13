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
    print("Received a request for recommendations for uid", uid)
    resp = dber.recommend_books(uid, num_recommendations=25)
    print(resp)
    return resp


@app.route('/gethistory/<uid>', methods=['GET'])
def get_history(uid):
    uid = int(uid)
    print("Received a request for recommendations for uid", uid)
    resp = dber.user_rating_history(uid)
    print(resp)
    return resp


if __name__ == '__main__':
    app.run()

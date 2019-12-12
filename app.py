from flask import Flask, request

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
    print("hello world")
    # TODO: implement
    # for testing: 1-10 return False (already taken), 10+ print to console
    print(uid)
    return True


if __name__ == '__main__':
    app.run()

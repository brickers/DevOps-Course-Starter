from flask import Flask, request
from flask.templating import render_template
from .data.session_items import get_items, add_item

from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return load_index()


def load_index():
    items = get_items()
    return render_template('index.html', items=items)


@app.route("/todos/submit", methods=['POST'])
def add_todo():
    add_item(request.form.get('title'))
    return load_index()


if __name__ == '__main__':
    app.run()

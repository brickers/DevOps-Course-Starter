from flask import Flask, request, redirect
from flask.templating import render_template
from .data.session_items import get_items, add_item
import requests
import os
import json

from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/todos/submit", methods=['POST'])
def add_todo():
    add_item(request.form.get('title'))
    return redirect("/")


if __name__ == '__main__':
    app.run()

BASE_URL = "https://api.trello.com"
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
auth_header = {
    "Authorization": f'OAuth oauth_consumer_key="{TRELLO_API_KEY}", oauth_token="{TRELLO_TOKEN}"'}

# show homepage with search for board title
# results will be a list of matching boards, with a link to /board/id
# /board/id will show our todos


@app.route('/search/boards', methods=['POST'])
def search_boards():
    url = BASE_URL + "/1/search"
    query = request.form.get('title')
    payload = {"query": query, "idBoards": "mine",
               "modelTypes": "boards", "partial": "true"}
    response = requests.get(url, params=payload, headers=auth_header)
    if response.ok:
        try:
            boards = response.json()["boards"]
            return render_template('boards.html', boards=boards)
        except:
            return redirect("/")


@app.route("/board/<id>")
def show_board(id):
    board = getBoard(id)
    lists = getBoardLists(id)

    for list in lists:
        cards = getListCards(list["id"])
        list["cards"] = cards

    board["lists"] = lists
    return render_template("board.html", board=board)


@app.route("/card/<cardId>/list/<listId>", methods=['POST'])
def moveCardToList(cardId, listId):
    card = getCard(cardId)
    idBoard = card['idBoard']
    card = {
        "idList": listId
    }
    url = BASE_URL + f"/1/cards/{cardId}"
    response = requests.put(url, params=card, headers=auth_header)
    if response.ok:
        return redirect(f"/board/{idBoard}")
    else:
        print('fuck')
        return


def getBoard(id):
    url = BASE_URL + f"/1/boards/{id}"
    board = getTrelloItem(url)
    return board


def getCard(id):
    url = BASE_URL + f"/1/cards/{id}"
    card = getTrelloItem(url)
    return card


def getBoardLists(id):
    url = BASE_URL + f"/1/boards/{id}/lists"
    lists = getTrelloItem(url)
    return lists


def getListCards(id):
    url = BASE_URL + f"/1/lists/{id}/cards"
    cards = getTrelloItem(url)
    return cards


def getTrelloItem(url):
    response = requests.get(url, headers=auth_header)
    if response.ok:
        try:
            item = response.json()
            return item
        except:
            pass

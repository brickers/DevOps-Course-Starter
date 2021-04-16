from flask import Flask, request, redirect
from flask.templating import render_template
import requests
import os

from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Global variables ------------------------------------------------------------
BASE_URL = "https://api.trello.com"
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
auth_header = {
    "Authorization": f'OAuth oauth_consumer_key="{TRELLO_API_KEY}", oauth_token="{TRELLO_TOKEN}"'}


# Routes ----------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/boards', methods=['POST'])
def search_boards():
    try:
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
    except:
        return render_template("error.html")


@app.route("/board/<id>")
def show_board(id):
    try:
        board = getBoard(id)
        lists = getBoardLists(id)

        for list in lists:
            cards = getListCards(list["id"])
            list["cards"] = cards

        board["lists"] = lists
        return render_template("board.html", board=board)
    except:
        return render_template("error.html")


# i would prefer this to be a PATCH route as we are only changing one part of
# the card object, but HTML forms can only submit GET and POST requests and I
# didn't want to start writing javascript

@app.route("/card/<cardId>/list/<listId>", methods=['POST'])
def moveCardToList(cardId, listId):
    try:
        card = getCard(cardId)
        card.moveToList(listId)
        if card.lastResponseOK:
            return redirect(f"/board/{card.getBoardID()}")
        else:
            raise RuntimeError  # ensures that the exception path is taken
    except:
        return render_template("error.html")


@app.route("/list/<idList>/card", methods=['POST'])
def addCardToList(idList):
    try:
        name = request.form.get('name')
        card = Card(name, idList)
        if card.lastResponseOK:
            return redirect(f"/board/{card.getBoardID()}")
        else:
            raise RuntimeError  # ensures that the exception path is taken
    except:
        return render_template("error.html")


# API helper functions --------------------------------------------------------


def getBoard(id):
    url = BASE_URL + f"/1/boards/{id}"
    return getTrelloItem(url)


def getCard(id):
    url = BASE_URL + f"/1/cards/{id}"
    return Card(getTrelloItem(url))


def getBoardLists(id):
    url = BASE_URL + f"/1/boards/{id}/lists"
    return getTrelloItem(url)


def getListCards(id):
    url = BASE_URL + f"/1/lists/{id}/cards"
    return getTrelloItem(url)


def getTrelloItem(url):
    response = requests.get(url, headers=auth_header)
    if response.ok:
        return response.json()


class Card:
    def __init__(self, *args):
        if len(args) > 1 and isinstance(args[0], str) and isinstance(args[1], str):
            self.name = args[0]
            self.idList = args[1]
            url = BASE_URL + f"/1/cards"
            params = {
                "name": self.name,
                "idList": self.idList
            }
            response = requests.post(url, params=params, headers=auth_header)
            self.idBoard = response.json()['idBoard']
            self.lastResponseOK = response.ok
        elif isinstance(args[0], dict):
            json = args[0]
            self.name = json["name"]
            self.id = json["id"]
            self.idList = json["idList"]
            self.idBoard = json["idBoard"]

    def moveToList(self, idList):
        self.idList = idList
        url = BASE_URL + f"/1/cards/{self.id}"
        params = self.getQueryParams()
        response = requests.put(url, params=params, headers=auth_header)
        self.lastResponseOK = response.ok

    def getQueryParams(self):
        result = {
            "name": self.name,
            "id": self.id,
            "idList": self.idList
        }
        return result

    def getBoardID(self):
        return self.idBoard

from flask import Flask, request, redirect
from flask.templating import render_template
import requests
import os

from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Global variables ------------------------------------------------------------
BASE_URL = "https://api.trello.com/1/"
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
        url = BASE_URL + "search"
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
        board = api_getBoard(id)
        lists = api_getBoardLists(id)

        for list in lists:
            cards = api_getListCards(list["id"])
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
        card = api_getCard(cardId)
        success = api_moveCardToList(card, listId)
        if success:
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
        success = api_createNewCard(card)
        if success:
            return redirect(f"/board/{card.getBoardID()}")
        else:
            raise RuntimeError  # ensures that the exception path is taken
    except:
        return render_template("error.html")


# API helper functions --------------------------------------------------------


def api_getBoard(id):
    url = BASE_URL + f"boards/{id}"
    return api_getItem(url)


def api_getCard(id):
    url = BASE_URL + f"cards/{id}"
    json = api_getItem(url)
    return Card(json["name"], json["idList"], json["id"], json["idBoard"])


def api_getBoardLists(id):
    url = BASE_URL + f"boards/{id}/lists"
    return api_getItem(url)


def api_getListCards(id):
    url = BASE_URL + f"lists/{id}/cards"
    return api_getItem(url)


def api_getItem(url):
    response = requests.get(url, headers=auth_header)
    if response.ok:
        return response.json()


def api_createNewCard(card):
    url = BASE_URL + f"cards"
    response = requests.post(
        url, params=card.getQueryParams(), headers=auth_header)
    card.setIdBoard(response.json()['idBoard'])
    return response.ok


def api_moveCardToList(card, idList):
    card.setIdList(idList)
    url = BASE_URL + f"cards/{card.id}"
    response = requests.put(
        url, params=card.getQueryParams(), headers=auth_header)
    return response.ok


class Card:
    def __init__(self, name, idList, idCard=None, idBoard=None):
        self.name = name
        self.idList = idList
        self.id = idCard
        self.idBoard = idBoard

    def setIdBoard(self, idBoard):
        self.idBoard = idBoard

    def setIdList(self, idList):
        self.idList = idList

    def getQueryParams(self):
        result = {
            "name": self.name,
            "id": self.id,
            "idList": self.idList
        }
        return result

    def getBoardID(self):
        return self.idBoard

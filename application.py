from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Room, Item, User
# TODO: add login session method to tie in OAuth

app = Flask(__name__, template_folder='./templates')

engine = create_engine('sqlite:///ItemCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

rooms = ['Living room', 'Dining Room', 'Bedroom', 'Bathroom']
items = [{'id': 1, 'name': 'couch', 'category': 'furniture', 'description': 'An item to sit on'}]

item = {'id': 1, 'name': 'couch', 'category': 'furniture', 'description': 'An item to sit on'}

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/rooms')
def showRooms():
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/<int:room_id>/edit', methods=['POST', 'GET'])
def editRoom(room_id):
    pass

@app.route('/rooms/<int:room_id>/delete')
def deleteRoom(room_id):
    pass

@app.route('/rooms/<int:room_id>/items')
def showItems(room_id):
    return render_template('items.html', items=items)

@app.route('/rooms/<int:room_id>/items/<int:item_id>')
def addItem(room_id):
    pass

@app.route('/rooms/<int:room_id>/items/<int:item_id>/edit')
def editItem(room_id, item_id):
    pass

@app.route('/rooms/<int:room_id>/items/<int:item_id>/delete')
def deleteItem(room_id, item_id):
    pass

@app.route('/itemcatalog.json')
def showAPI():
    pass

# Add endpoints for login?... API connection with json and database
# render redirects/urls for login, each room, items and info in that room
# extendable data for suggestions later??

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)

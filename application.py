from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Room, Item, User
# TODO: add login session method to tie in OAuth, maybe csrf protection

app = Flask(__name__)

engine = create_engine('sqlite:///useritemcatalog.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# rooms = [{'id': 1, 'name': 'Living room'}, {'id': 2, 'name': 'Dining Room'}, {'id': 3, 'name': 'Bedroom'}, {'id': 4, 'name': 'Bathroom'}]
#items = [{'id': 1, 'name': 'couch', 'category': 'furniture', 'description': 'An item to sit on'}, {'id': 2, 'name': 'test', 'category': 'furnituretest', 'description': 'An item to test on'}]
# item = {'name': 'couch', 'category': 'furniture', 'description': 'An item to sit on'}

# need database to handle id number by order???
# rooms = session.query(Room).all()

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/rooms')
def showRooms():
    rooms = session.query(Room).all()
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/new', methods=['GET', 'POST'])
def newRoom():
    if request.method == 'POST':
        newRoom = Room(name=request.form['name'], id=request.form['id'])
        session.add(newRoom)
        session.commit()
        return redirect(url_for('showRooms'))
    else:
        return render_template('newroom.html')

@app.route('/rooms/<int:room_id>/edit', methods=['POST', 'GET'])
def editRoom(room_id):
    roomToEdit = session.query(Room).filter_by(id=room_id).one()
    if request.method == 'POST':
        if request.form['name']:
            roomToEdit.name = request.form['name']
        if request.form['id']:
            roomToEdit.id = request.form['id']
        session.add(roomToEdit)
        session.commit()
        return redirect(url_for('showRooms'))
    else:
        return render_template('editroom.html', room_id=room_id, room = roomToEdit)

@app.route('/rooms/<int:room_id>/delete', methods=['POST', 'GET'])
def deleteRoom(room_id):
    roomToDelete = session.query(Room).filter_by(id=room_id).one()
    if request.method == 'POST':
        session.delete(roomToDelete)
        session.commit()
        return redirect(url_for('showRooms'))
    else:
        return render_template('deleteroom.html', room_id=room_id)

@app.route('/rooms/<int:room_id>/items')
@app.route('/rooms/<int:room_id>')
def showItems(room_id):
    items = session.query(Item).filter_by(id=room_id).all()
    return render_template('items.html', items=items)

@app.route('/rooms/<int:room_id>/items/new', methods=['POST', 'GET'])
def newItem(room_id):
    items = session.query(Item).all()
    if request.method == 'POST':
        itemToAdd = Item(name=request.form['name'], category=request.form['category'], description=request.form['description'])
        session.add(itemToAdd)
        session.commit()
        return redirect(url_for('showItems', room_id=room_id, items=items))
    else:
        return render_template('newitem.html', room_id = room_id)

@app.route('/rooms/<int:room_id>/items/<int:item_id>/edit', methods=['POST', 'GET'])
def editItem(room_id, item_id):
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        if request.form['category']:
            itemToEdit.category = request.form['category']
        session.add(itemToEdit)
        session.commit()
        return redirect(url_for('showItems', room_id=room_id))
    else:
        return render_template('editItem.html', room_id=room_id, item_id=item_id, item=itemToEdit)

@app.route('/rooms/<int:room_id>/items/<int:item_id>/delete', methods=['POST', 'GET'])
def deleteItem(room_id, item_id):
    return "This page allows users to delete an item"

@app.route('/itemcatalog.json')
def showAPI():
    return "Page for the JSON data for rooms/items"

# Add endpoints for login?... API connection with json and database
# render redirects/urls for login, each room, items and info in that room
# extendable data for suggestions later??

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)

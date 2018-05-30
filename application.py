from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, session as user_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Room, Item, User
import logging
import os
# TODO: add login session method to tie in OAuth, maybe csrf protection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
engine = create_engine('sqlite:///useritemcatalog.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def home():
    if not user_session.get('logged_in'):
        return render_template('login.html')
    else:
        return showRooms()

@app.route('/login', methods=['POST'])
def do_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        user_session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/logout')
def logout():
    user_session['logged_in'] = False
    return home()

@app.route('/rooms/')
def showRooms():
    rooms = session.query(Room).all()
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/new', methods=['GET', 'POST'])
def newRoom():
    if request.method == 'POST':
        newRoom = Room(name=request.form['name'])
        session.add(newRoom)
        session.commit()
        return redirect(url_for('showRooms'))
    else:
        return render_template('newroom.html')

@app.route('/rooms/<int:room_id>/edit', methods=['POST', 'GET'])
def editRoom(room_id):
    try:
        roomToEdit = session.query(Room).filter_by(id=room_id).one()
        if request.method == 'POST':
            if request.form['name']:
                roomToEdit.name = request.form['name']
            session.add(roomToEdit)
            session.commit()
            return redirect(url_for('showRooms'))
        else:
            return render_template('editroom.html', room_id=room_id, room = roomToEdit)
    except:
        return 'Could not find that room', 404

@app.route('/rooms/<int:room_id>/delete', methods=['POST', 'GET'])
def deleteRoom(room_id):
    roomToDelete = session.query(Room).filter_by(id=room_id).one()
    if request.method == 'POST':
        session.delete(roomToDelete)
        session.commit()
        return redirect(url_for('showRooms'))
    else:
        return render_template('deleteroom.html', room_id=room_id, room=roomToDelete)

@app.route('/rooms/<int:room_id>/items')
@app.route('/rooms/<int:room_id>')
def showItems(room_id):
    room = session.query(Room).filter_by(id=room_id).one()
    items = session.query(Item).filter_by(room_id=room_id).all()
    return render_template('items.html', items=items, room=room, room_id=room_id)

@app.route('/rooms/<int:room_id>/items/new', methods=['POST', 'GET'])
def newItem(room_id):
    if request.method == 'POST':
        itemToAdd = Item(name=request.form['name'], category=request.form['category'], description=request.form['description'], room_id=room_id)
        session.add(itemToAdd)
        session.commit()
        return redirect(url_for('showItems', room_id=room_id))
    else:
        return render_template('newitem.html', room_id = room_id)

@app.route('/rooms/<int:room_id>/items/<int:item_id>/edit', methods=['POST', 'GET'])
def editItem(room_id, item_id):
    itemToEdit = session.query(Item).filter_by(room_id=room_id, id=item_id).one()
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
        return render_template('edititem.html', room_id=room_id, item_id=item_id, item=itemToEdit)

@app.route('/rooms/<int:room_id>/items/<int:item_id>/delete', methods=['POST', 'GET'])
def deleteItem(room_id, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', room_id=room_id))
    else:
        return render_template('deleteitem.html', room_id=room_id, item_id=item_id, item=itemToDelete)

@app.route('/itemcatalog.json')
def showAPI():
    return "Page for the JSON data for rooms/items"

# Add endpoints for login?... API connection with json and database
# render redirects/urls for login, each room, items and info in that room
# extendable data for suggestions later??

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=8001, debug=True)

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, session as login_session, make_response
# from flask_login import login_manager, LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Room, Item, User
import random, string, httplib2, json, requests, ConfigParser
# import logging
import os
# from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

app = Flask(__name__)
engine = create_engine('sqlite:///useritemcatalog.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

# user_datastore = SQLAlchemySessionUserDatastore(session, User)
# security = Security(app, user_datastore)

DBSession = sessionmaker(bind=engine)
session = DBSession()

#TODO: Create user and get user id/ info; protect pages that require login- CUD, not R

# @app.before_first_request
# def create_user():
#    new_user = user_datastore.create_user(email='', password='')
#    session.commit()

#TODO: Adjust for OAuth method, show welcome page that sends to login
@app.route('/')
def home():
    if not login_session.get('logged_in'):
        return render_template('login.html')
    else:
        return showRooms()

#TODO: Make sure each room/item is specific user's own via login_session['id' or 'username']
@app.route('/login', methods=['GET', 'POST'])
def do_login():

    valid = (string.ascii_letters, string.digits, ':*&^')

    def gen_random_string(valid, length):
        random_string = ''.join(valid) # join together members of tuple which is iterable
        return ''.join(random.choice(random_string) for x in xrange(length)) # returns a random string w/ length chars
    
    state = gen_random_string(valid, 32) # set state to the result of the func

    login_session['state'] = state # passing value of state to the login_session- preventing CSF attacks
    
    # if request.form['password'] == 'password' and request.form['username'] == 'admin':
    #     login_session['logged_in'] = True
    #     flash('Logged in!')
    # else:
    #     flash('Invalid Login!')
    # return home()
    

    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # user_id = getUserID(login_session['email'])
    # if not user_id:
    #     user_id = createUser(login_session)
    # login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# To be changed, password or picture stored?
def createUser():
    newUser = User(name=login_session['username'], email=login_session['email'], password=login_session['gplus_id'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/logout') #TODO: Disconnects and shows welcome page again
def logout():
    login_session['logged_in'] = False
    return home()

@app.route('/rooms/')
def showRooms():
    rooms = session.query(Room).all()
    return render_template('rooms.html', rooms=rooms)
#TODO: add login_required to any new, updated, deleted room/ items
@app.route('/rooms/new', methods=['GET', 'POST'])
def newRoom():
    if request.method == 'POST':
        newRoom = Room(name=request.form['name']) # will add line user_id = login_session['user_id] to Room
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

# serialize- JSONIFY, for the API endpoint?

if __name__ == '__main__':
    app.secret_key = os.urandom(12)

    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # login_manager.login_view = 'do_login'

    app.run(host='0.0.0.0', port=8001, debug=True)
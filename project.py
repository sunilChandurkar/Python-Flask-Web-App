from flask import Flask, session, render_template, request, redirect, jsonify, url_for, flash
from database_setup import Base, User, Category, Item

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)



# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
dbsession = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['GET', 'POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token
    
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    
    print "app_id is %s " % app_id
    print "app_secret is %s " % app_secret
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "result is %s" % result
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]

    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists by username
    user_id = getUserID(login_session['username'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    session["loggedin"]=True
    session["username"]=login_session['username']
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    session["loggedin"]=False
    session["username"]=None
    flash("You have been logged out.")
    return redirect(url_for('showCategories'))
    #return redirect(url_for('/')

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    dbsession.add(newUser)
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = dbsession.query(User).filter_by(id=user_id).one()
    return user


def getUserID(name):
    try:
        user = dbsession.query(User).filter_by(name=name).one()
        return user.id
    except:
        return None



# Show all categories
@app.route('/')
def showCategories():
    #return "This Page will show Categories and Latest Items."
    categories = dbsession.query(Category).all()
    items = dbsession.query(Item).order_by(desc(Item.id)).limit(8)
    users = dbsession.query(User).all()

    return render_template('home.html', categories=categories, users=users, items=items)

#Show items in a specific category
@app.route('/catalog/<string:category>/items')
def showCategory(category):
    #get all categories
    categories = dbsession.query(Category).all()
    #get the specified category
    category = dbsession.query(Category).filter_by(name=category).one()
    items = dbsession.query(Item).filter_by(category_id=category.id)
    return render_template('category.html', category=category, categories=categories, items=items)

#Show a specific item
@app.route('/catalog/<string:category>/<string:item>')
def showItem(item, category):
    #return "This item is a %s ." % item
    #print item
    myitem = dbsession.query(Item).filter_by(title=item).one()
    #print myitem
    return render_template('item.html', category=category, item=myitem)

#Create an item
@app.route('/catalog/item/create', methods=['GET', 'POST'])
def createItem():
    #if user is not logged in show error
    if not session["loggedin"]:
        flash("Only Logged In Users can Add Items. Please Log In.")
        return render_template("error.html")
    #Get the user id of the logged in user
    user_id = getUserID(session["username"])
    if request.method == 'POST':
        item = Item(title=request.form["title"], description=request.form['description'],
                     category_id=request.form["category_id"], user_id=user_id)
        dbsession.add(item)
        dbsession.commit()
        flash("a new item has been added")
        return redirect(url_for('showCategories'))
    else:
        categories = dbsession.query(Category).all()
        return render_template('additem.html', categories=categories)

#Edit an Item
@app.route('/catalog/<string:item>/edit', methods=['GET', 'POST'])
def editItem(item):
    #show error if user is not logged in
    if not session["loggedin"]:
        flash("Only Logged In Users can Edit Items. Please Log In.")
        return render_template("error.html")

    #retrieve user id
    user_id = getUserID(session["username"])
    #retrieve item
    myItem = dbsession.query(Item).filter_by(title=item).one()

    #if item has not been created by logged in user show error
    if myItem.user_id != user_id:
        flash("You can only edit items you have created.")
        return render_template("error.html")  

    if request.method == 'POST':

        myItem.title = request.form["title"]
        myItem.description = request.form['description']
        myItem.category_id=request.form["category_id"]
        dbsession.add(myItem)
        dbsession.commit()
        #flash("an item has been edited")   
        return redirect(url_for('showItem', item=myItem.title, category=myItem.category.name))
    else: 
        categories = dbsession.query(Category).all()
        return render_template('edititem.html', item=myItem, categories=categories)

#Delete an Item
@app.route('/catalog/<string:item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
    #return "This page will delete a %s ." % item
    if not session["loggedin"]:
        flash("Only Logged In Users can Delete Items. Please Log In.")
        return render_template("error.html")

    user_id = getUserID(session["username"])
    myItem = dbsession.query(Item).filter_by(title=item).one()

    #if item has not been created by logged in user show error
    if myItem.user_id != user_id:
        flash("You can only delete items you have created.")
        return render_template("error.html")  

    if request.method == 'POST':
        dbsession.delete(myItem)
        dbsession.commit()
        flash("item has been deleted") 
        return redirect(url_for('showCategories')) 
    else:         
        return render_template('deleteitem.html', item=myItem)

#API Endpoint
@app.route('/catalog/<string:category>/<string:item>/JSON')
def ItemJSON(category, item):
    category = dbsession.query(Category).filter_by(name=category).one()
    item = dbsession.query(Item).filter_by(title=item).one()
    return jsonify(Category=category.serialize, Item = item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
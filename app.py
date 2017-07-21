from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, Stock

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Department Stock Inventory"

engine = create_engine('sqlite:///stock_inventory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
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

# Add JSON endpoint
@app.route('/departments/<department_id>/stock/json')
def departmentStockJSON(department_id):
    department = session.query(Department).filter_by(id=department_id).one()
    stocks = session.query(Stock).filter_by(department_id=department.id)
    return jsonify(Stock=[i.serialize for i in stocks])

@app.route('/departments/<department_id>/stock/<int:stock_id>/json')
def stockJSON(department_id, stock_id):
    stock = session.query(Stock).filter_by(id=stock_id).one()
    return jsonify(Stock=stock.serialize)

@app.route('/departments/json')
def departmentsJSON():
    depts = session.query(Department).all()
    return jsonify(Department=[dept.serialize for dept in depts])


@app.route('/')
@app.route('/departments')
def showDepartments():
    departments = session.query(Department).all()
    return render_template('departments.html', departments=departments)

# Create a new Department
@app.route('/departments/new/', methods=['GET', 'POST'])
def newDepartment():
    if request.method == 'POST':
        newDepartment = Department(name=request.form['name'])
        session.add(newDepartment)
        session.commit()
        return redirect(url_for('showDepartments'))
    else:
        return render_template('new_department.html')
    # return "This page will be for making a new department"


@app.route('/departments/<department_id>/stock')
def departmentStock(department_id):
    department = session.query(Department).filter_by(id=department_id).one()
    stocks = session.query(Stock).filter_by(department_id=department.id)
    return render_template('stock.html', department=department, stocks=stocks)

@app.route('/departments/<int:department_id>/new/', methods=['GET', 'POST'])
def newStock(department_id):
    if request.method == 'POST':
        newStock = Stock(
            name=request.form['name'], brand=request.form['brand'], num_in_stock=request.form['num_in_stock'],
            department_id=department_id)
        session.add(newStock)
        session.commit()
        flash("new stock item created")
        return redirect(url_for('departmentStock', department_id=department_id))
    else:
        return render_template('new_stock.html', department_id=department_id)


@app.route('/departments/<int:department_id>/<int:stock_id>/edit/', methods=['GET', 'POST'])
def editStockItem(department_id, stock_id):
    editedStock = session.query(Stock).filter_by(id=stock_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedStock.name = request.form['name']
        if request.form['brand']:
            editedStock.brand = request.form['brand']
        if request.form['num_in_stock']:
            editedStock.num_in_stock = request.form['num_in_stock']
        session.add(editedStock)
        session.commit()
        flash("new stock item edited")
        return redirect(url_for('departmentStock', department_id=department_id))
    else:
        return render_template(
            'edit_stock.html', department_id=department_id, stock_id=stock_id, stock=editedStock)



@app.route('/departments/<int:department_id>/<int:stock_id>/delete/', methods=['GET', 'POST'])
def deleteStockItem(department_id, stock_id):
    itemToDelete = session.query(Stock).filter_by(id=stock_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("new stock item deleted")
        return redirect(url_for('departmentStock', department_id=department_id))
    else:
        return render_template('delete_stock.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'this_is_secret'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
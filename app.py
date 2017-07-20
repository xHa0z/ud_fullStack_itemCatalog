from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, Stock

app = Flask(__name__)

engine = create_engine('sqlite:///stock_inventory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/departments/<department_id>/')
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
        return redirect(url_for('departmentStock', department_id=department_id))
    else:
        return render_template('delete_stock.html', item=itemToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
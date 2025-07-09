from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.client import Client

client_bp = Blueprint('client', __name__)

@client_bp.route('/')
def list_clients():
    """List all clients"""
    clients = Client.get_all_clients()
    return render_template('clients/list.html', clients=clients)

@client_bp.route('/add', methods=['GET', 'POST'])
def add_client():
    """Add a new client"""
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'address': request.form['address'],
            'email': request.form['email'],
            'phone': request.form['phone']
        }
        
        try:
            Client.create_client(data)
            flash('Client added successfully!', 'success')
            return redirect(url_for('client.list_clients'))
        except Exception as e:
            flash(f'Error adding client: {str(e)}', 'error')
    
    return render_template('clients/add.html')

@client_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """Edit an existing client"""
    client = Client.get_client_by_id(client_id)
    if not client:
        flash('Client not found!', 'error')
        return redirect(url_for('client.list_clients'))
    
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'address': request.form['address'],
            'email': request.form['email'],
            'phone': request.form['phone']
        }
        
        try:
            Client.update_client(client_id, data)
            flash('Client updated successfully!', 'success')
            return redirect(url_for('client.list_clients'))
        except Exception as e:
            flash(f'Error updating client: {str(e)}', 'error')
    
    return render_template('clients/edit.html', client=client)

@client_bp.route('/delete/<int:client_id>')
def delete_client(client_id):
    """Delete a client"""
    try:
        success, message = Client.delete_client(client_id)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    except Exception as e:
        flash(f'Error deleting client: {str(e)}', 'error')
    
    return redirect(url_for('client.list_clients'))

@client_bp.route('/view/<int:client_id>')
def view_client(client_id):
    """View client details"""
    client = Client.get_client_by_id(client_id)
    if not client:
        flash('Client not found!', 'error')
        return redirect(url_for('client.list_clients'))
    
    return render_template('clients/view.html', client=client)
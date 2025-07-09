from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.contractor import Contractor

contractor_bp = Blueprint('contractor', __name__)

@contractor_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup contractor information"""
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'address': request.form['address'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'tax_id': request.form['tax_id'],
            'personal_tax_id': request.form['personal_tax_id']
        }
        
        try:
            Contractor.create_or_update_contractor(data)
            flash('Contractor information saved successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Error saving contractor information: {str(e)}', 'error')
    
    # Get existing contractor info
    contractor = Contractor.get_contractor()
    
    return render_template('contractor/setup.html', contractor=contractor)

@contractor_bp.route('/info')
def info():
    """View contractor information"""
    contractor = Contractor.get_contractor()
    if not contractor:
        flash('Please setup contractor information first!', 'warning')
        return redirect(url_for('contractor.setup'))
    
    return render_template('contractor/info.html', contractor=contractor)
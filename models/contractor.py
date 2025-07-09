from models.database import execute_query

class Contractor:
    def __init__(self, name, address=None, email=None, phone=None, tax_id=None, personal_tax_id=None):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.tax_id = tax_id
        self.personal_tax_id = personal_tax_id
    
    @staticmethod
    def get_contractor():
        """Get the contractor information (assuming single contractor)"""
        query = "SELECT * FROM contractor_info LIMIT 1"
        return execute_query(query, fetch='one')
    
    @staticmethod
    def create_or_update_contractor(data):
        """Create or update contractor information"""
        existing = Contractor.get_contractor()
        
        if existing:
            query = '''
                UPDATE contractor_info 
                SET name=?, address=?, email=?, phone=?, tax_id=?, personal_tax_id=?
                WHERE id=?
            '''
            params = (
                data['name'], data['address'], data['email'], 
                data['phone'], data['tax_id'], data['personal_tax_id'], 
                existing['id']
            )
        else:
            query = '''
                INSERT INTO contractor_info (name, address, email, phone, tax_id, personal_tax_id)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['name'], data['address'], data['email'], 
                data['phone'], data['tax_id'], data['personal_tax_id']
            )
        
        return execute_query(query, params)
    
    @staticmethod
    def get_contractor_dict():
        """Get contractor information as dictionary"""
        contractor = Contractor.get_contractor()
        if contractor:
            return {
                'id': contractor['id'],
                'name': contractor['name'],
                'address': contractor['address'],
                'email': contractor['email'],
                'phone': contractor['phone'],
                'tax_id': contractor['tax_id'],
                'personal_tax_id': contractor['personal_tax_id']
            }
        return None
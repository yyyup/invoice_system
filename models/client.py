from models.database import execute_query

class Client:
    def __init__(self, name, address=None, email=None, phone=None):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
    
    @staticmethod
    def get_all_clients():
        """Get all clients ordered by name"""
        query = "SELECT * FROM clients ORDER BY name"
        return execute_query(query, fetch='all')
    
    @staticmethod
    def get_client_by_id(client_id):
        """Get client by ID"""
        query = "SELECT * FROM clients WHERE id = ?"
        return execute_query(query, (client_id,), fetch='one')
    
    @staticmethod
    def create_client(data):
        """Create a new client"""
        query = '''
            INSERT INTO clients (name, address, email, phone)
            VALUES (?, ?, ?, ?)
        '''
        params = (data['name'], data['address'], data['email'], data['phone'])
        return execute_query(query, params)
    
    @staticmethod
    def update_client(client_id, data):
        """Update an existing client"""
        query = '''
            UPDATE clients 
            SET name=?, address=?, email=?, phone=?
            WHERE id=?
        '''
        params = (data['name'], data['address'], data['email'], data['phone'], client_id)
        return execute_query(query, params)
    
    @staticmethod
    def delete_client(client_id):
        """Delete a client (if no invoices exist)"""
        # Check if client has invoices
        check_query = "SELECT COUNT(*) as count FROM invoices WHERE client_id = ?"
        result = execute_query(check_query, (client_id,), fetch='one')
        
        if result['count'] > 0:
            return False, "Cannot delete client with existing invoices"
        
        query = "DELETE FROM clients WHERE id = ?"
        execute_query(query, (client_id,))
        return True, "Client deleted successfully"
    
    @staticmethod
    def get_clients_for_dropdown():
        """Get clients formatted for dropdown selection"""
        clients = Client.get_all_clients()
        return [(client['id'], client['name']) for client in clients]
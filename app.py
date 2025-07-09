from flask import Flask
from config import Config
from models.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    init_db()
    
    # Register blueprints
    from routes.main import main_bp
    from routes.contractor import contractor_bp
    from routes.client import client_bp
    from routes.invoice import invoice_bp
    from routes.receipt import receipt_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(contractor_bp, url_prefix='/contractor')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(invoice_bp, url_prefix='/invoice')
    app.register_blueprint(receipt_bp, url_prefix='/receipt')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
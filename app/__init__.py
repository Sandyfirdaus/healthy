from flask import Flask
from config import Config
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client[app.config['DBNAME']]
    
    # Import and register Blueprints
    from .routes import (
        home, artikeldepan, artikeldepan_details, homesignin, auth, auth_admin,
        dashboard, program, program_content, program_details, artikel,
        artikel_details, profile
    )
    
    blueprints = [
        home.home_,
        artikeldepan.artikeldepan_,
        artikeldepan_details.artikeldepan_details_,
        homesignin.homesignin_,
        auth.auth_,
        auth_admin.auth_admin_,
        dashboard.dashboard_,
        program.program_,
        program_content.program_content_,
        program_details.program_details_,
        artikel.artikel_,
        artikel_details.artikel_details_,
        profile.profile_
    ]
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    return app

from flask import Flask
from config import Config
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB
    client = MongoClient(app.config["MONGODB_URI"])
    app.db = client[app.config["DBNAME"]]
    
    # Import Blueprints
    from .routes import (
        home, artikeldepan, artikeldepan_details, homesignin, auth, auth_admin,
        dashboard, add_articles, add_program, program, program_content, 
        program_details, artikel, artikel_details, profile
    )
    
    # List of Blueprints
    blueprints = [
        home.home_,
        artikeldepan.artikeldepan_,
        artikeldepan_details.artikeldepan_details_,
        homesignin.homesignin_,
        auth.auth_,
        auth_admin.auth_admin_,
        dashboard.dashboard_,
        add_articles.add_articles_,
        add_program.add_program_,
        program.program_,
        program_content.program_content_,
        program_details.program_details_,
        artikel.artikel_,
        artikel_details.artikel_details_,
        profile.profile_
    ]
    
    # Register Blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    return app

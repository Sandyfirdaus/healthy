from flask import Flask
from config import Config
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
     
    # MONGODB
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client[app.config['DBNAME']]
    
    from .routes.home import home_
    app.register_blueprint(home_)

    from .routes.homesignin import homesignin_
    app.register_blueprint(homesignin_)

    from .routes.auth import auth_
    app.register_blueprint(auth_)

    from .routes.program import program_
    app.register_blueprint(program_)
    
    from .routes.program_content import program_content_
    app.register_blueprint(program_content_)
    
    from .routes.program_details import program_details_
    app.register_blueprint(program_details_)
    
    from .routes.artikel import artikel_
    app.register_blueprint(artikel_)
    
    from .routes.artikel_details import artikel_details_
    app.register_blueprint(artikel_details_)
    
    from .routes.profile import profile_
    app.register_blueprint(profile_)

    return app

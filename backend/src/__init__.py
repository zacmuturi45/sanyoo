from flask import Flask, request
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_migrate import Migrate
from .schema import schema
from .models import db, Patient, Doctor, Assessment, Prescription, Inventory
from .config import config

migrate = Migrate()

import sys
print(sys.path)

jwt = JWTManager()

def create_app(config_name="default"):
    
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    CORS(app)
    
    migrate.init_app(app, db)
    
    jwt.init_app(app)
    
    class CustomGraphQLView(GraphQLView):
        def get_context(self):
            user_id = None
            if "Authorization" in request.headers:
                token = request.headers.get("Authorization").split(" ")[1]
                user_id = get_jwt_identity()
            return { "user_id": user_id }
    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
    )
    
    return app
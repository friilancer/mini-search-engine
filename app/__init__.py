from flask import Flask
from indexer.indexer import create_index, index_data




def create_app():
    app = Flask(__name__)

    search_index = create_index()
    #index the crawled data
    index_data(search_index)
    app.config["SEARCH_INDEX"] = search_index

    from .routes import crawler_bp
    app.register_blueprint(crawler_bp)

    return app
from flask import Flask
from indexer.indexer import create_index, index_data
from crawler.crawler import crawl_all_domains
from .routes import crawler_bp
import os

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_path = os.path.join(base_dir, '..', 'templates')
    
    app = Flask(__name__, template_folder=templates_path)

    crawl_all_domains()
    
    search_index = create_index()

    searcher = search_index.searcher()

    app.config["SEARCH_INDEX"] = search_index
    app.config["SEARCHER"] = searcher

    index_data(search_index)
    
    app.register_blueprint(crawler_bp)

    return app
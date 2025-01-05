from flask import Flask
from indexer.indexer import create_index, index_data
from crawler.crawler import crawl_all_domains
from .routes import crawler_bp
import os


def create_app():
    # app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_path = os.path.join(base_dir, '..', 'templates')
    SEARCH_THREADS = int(os.getenv("SEARCH_THREADS", 2))
    
    app = Flask(__name__, template_folder=templates_path)

    # crawl_all_domains()
    
    search_index = create_index()

    # searcher = search_index.searcher(num_threads=SEARCH_THREADS)
    searcher = search_index.searcher()

    # Store in app.config so routes can access them
    app.config["SEARCH_INDEX"] = search_index
    app.config["SEARCHER"] = searcher
    #index the crawled data
    index_data(search_index)
    
    app.register_blueprint(crawler_bp)

    return app
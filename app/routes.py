from flask import Blueprint, jsonify, request, render_template, current_app
from crawler.crawler import crawl_all_domains
from indexer.indexer import create_index
import os
from dotenv import load_dotenv


load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH")
SEARCH_THREADS = os.getenv("SEARCH_THREADS")
crawler_bp = Blueprint('crawler', __name__)


@crawler_bp.route('/crawl', methods=["POST"])
def trigger_crawler():
    try:
        crawl_all_domains()
        return jsonify({
            "message": "Crawling started", 
        }), 200

    except Exception as e:
        return jsonify({"error", str(e)}), 500

@crawler_bp.route('/search', methods=["GET"])
def search():
    query = request.args.get("q")
    print(f"query: {query}")
    if not query:
        return jsonify({"error" : "Query parameter is required"}), 400
    search_index = current_app.config["SEARCH_INDEX"]
    searcher = current_app.config["SEARCHER"]
    # search_index = create_index()
    search_index.reload()
    
    search_query = search_index.parse_query(query)
    results = searcher.search(search_query, 15) 

    response = []
    for hit in results.hits:
        print(f"The hit: {hit}")
        (best_score, best_doc_address) = hit
        best_doc = searcher.doc(best_doc_address)

        print(f"Address: {best_doc_address} : {best_doc}")

        response.append({
            "title" :  best_doc["title"],
            "url" :  best_doc["url"],
            "snippet" :  best_doc["snippet"],
        })

    return jsonify(response)

@crawler_bp.route("/", methods=["GET"])
def home():
    return render_template('search.html')

@crawler_bp.route("/stat", methods=["GET"])
def home():
    return render_template('stat.html')
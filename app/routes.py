from flask import Blueprint, jsonify, request, render_template, current_app
from crawler.crawler import crawl_all_domains
from indexer.indexer import create_index, index_data
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH")
SEARCH_THREADS = os.getenv("SEARCH_THREADS")
crawler_bp = Blueprint('crawler', __name__)


@crawler_bp.route('/api/crawl', methods=["POST"])
def trigger_crawler():
    try:
        crawl_all_domains()
        return jsonify({
            "message": "Crawling started", 
        }), 200

    except Exception as e:
        return jsonify({"error", str(e)}), 500

@crawler_bp.route('/api/search', methods=["GET"])
def search():
    query = request.args.get("q")
    print(f"query: {query}")
    if not query:
        return jsonify({"error" : "Query parameter is required"}), 400
    search_index = current_app.config["SEARCH_INDEX"]
    searcher = current_app.config["SEARCHER"]
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

@crawler_bp.route('/api/stats', methods=['GET'])
def stats():
    conn = sqlite3.connect("crawler/crawled_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pages")
    total_pages = cursor.fetchone()[0] or 0

    cursor.execute("SELECT domain, COUNT(*) FROM pages GROUP BY domain")
    domain_counts = cursor.fetchall()
    conn.close()

    domain_data = [
        {"domain": row[0] if row[0] else "Unknown", "count": row[1]} 
        for row in domain_counts
    ]

    return jsonify({
        "total_pages": total_pages,
        "domain_counts": domain_data
    })

@crawler_bp.route('/api/index', methods=['GET'])
def index():
    try:

        search_index = create_index()

        searcher = search_index.searcher()

        current_app.config["SEARCH_INDEX"] = search_index
        current_app.config["SEARCHER"] = searcher
        index_data(search_index)
        search_index.reload()
        return jsonify({
            "message": "Indexed", 
        }), 200

    except Exception as e:
        return jsonify({"error", str(e)}), 500

##Pages
@crawler_bp.route("/stats", methods=["GET"])
def statsPage():
    return render_template('stat.html')

@crawler_bp.route("/", methods=["GET"])
def homePage():
    return render_template('search.html')


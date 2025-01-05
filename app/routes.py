from flask import Blueprint, jsonify, request, render_template
from crawler.crawler import crawl_all_domains
from indexer.indexer import create_index
import os
from dotenv import load_dotenv


load_dotenv()

INDEX_PATH = os.getenv("INDEX_PATH")
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
    search_index = create_index()
    # search_index.reload()
    searcher = search_index.searcher()
    search_query = search_index.parse_query(query)#, ["title", "body"])
    results = searcher.search(search_query, 10) # Retrieve top 10 results

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
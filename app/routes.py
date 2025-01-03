from flask import Blueprint, jsonify, request
from crawler.crawler import crawl_domain
from indexer.indexer import create_index
import tantivy

crawler_bp = Blueprint('crawler', __name__)
INDEX_PATH = "indexer/search_index/"

@crawler_bp.route('/crawl', methods=["POST"])
def trigger_crawler():
    data = request.json
    start_url = data.get('start_url')
    max_pages = data.get('max_pages')

    if not start_url:
        return jsonify({"error": "start_url is required"}), 400
    
    try:
        crawl_domain(start_url, max_pages)
        return jsonify({
            "message": "Crawling started", 
            "start_url": start_url
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
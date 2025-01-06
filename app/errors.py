from flask import jsonify

def page_not_found(e):
        return jsonify({"error": "This route is not defined on the server."}), 404


def server_error(e):
        return jsonify({"error": "server error."}), 500

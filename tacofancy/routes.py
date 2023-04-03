from flask import jsonify, Blueprint, request, current_app

from ariadne import graphql_sync

from .graphql import explorer_html, schema


routes = Blueprint("routes", __name__, template_folder="templates")

@routes.route("/graphql", methods=["GET"])
def graphql_explorer():
    return explorer_html, 200


@routes.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=current_app.debug
    )

    if success:
        status_code = 200
    else:
        status_code = 400

    return jsonify(result), status_code

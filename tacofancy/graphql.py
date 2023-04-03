from ariadne import QueryType, graphql_sync, make_executable_schema
from ariadne.explorer import ExplorerGraphiQL


type_defs = """
    type Query {
        hello: String!    
    }
"""

query = QueryType()
schema = make_executable_schema(type_defs, query)
explorer_html = ExplorerGraphiQL().html(None)


@query.field("hello")
def resolve_hello(_, info):
    request = info.context
    user_agent = request.headers.get("User-Agent", "Guest")
    return "Hello, %s" % user_agent

from flask import jsonify

from ariadne import QueryType, graphql_sync, make_executable_schema, load_schema_from_path
from ariadne.explorer import ExplorerGraphiQL

from .db import db
from .models import BaseLayer, Condiment, Mixin, Seasoning, Shell, FullTaco


query = QueryType()
type_defs = load_schema_from_path("tacofancy/schema.graphql")


@query.field("base_layers")
def resolve_base_layers(_, info):
    base_layers = BaseLayer.query.all()
    return [b.as_dict() for b in base_layers]


@query.field("base_layer")
def resolve_base_layer(*_, slug=None):
    base_layer = BaseLayer.query.filter_by(slug=slug).first()
    if base_layer:
        return base_layer.as_dict()


schema = make_executable_schema(type_defs, query)
explorer_html = ExplorerGraphiQL().html(None)

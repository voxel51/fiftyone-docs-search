import fiftyone.operators as foo
import fiftyone.operators.types as types

from fiftyone.docs_search.query_index import query_index


class SearchDocs(foo.DynamicOperator):
  def __init__(self):
    super().__init__(
      "@voxel51/search-docs",
      "Search the FiftyOne docs",
    )
  
  def resolve_input(self, ctx):
    inputs = types.Object()
    inputs.str("query", label="Query", required=True)
    return types.Property(inputs)

  def execute(self, ctx):
    results = query_index(
        ctx.params.get("query")
    )
    links = []
    for url, text, score in results:
      links.append({
        "href": url,
        "label": text
      })
    return {"links": links}

  def resolve_output(self, ctx):
    outputs = types.Object()
    outputs.define_property("links", types.List(types.Link()))
    return types.Property(outputs)


op = None

def register():
  op = SearchDocs()
  foo.register_operator(op)

def unregister():
  foo.unregister_operator(op)

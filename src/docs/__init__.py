from .helpers import decode_type
from .constants import route_attrs, build_route_attrs
from webargs import missing


def decode_webargs(route, method, _auth="jwt", args=None):
    if not (args or _auth):
      return ""

    docs = """
parameters:"""

    if _auth and _auth.endswith("jwt"):
        docs += """
  - name: Authorization
    in: header
    description: JWT token for authentication.
    required: true
    type: string
    example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."""

    if ">" in route:
      slug = route.split("<")[1].split(">")
      docs += f"""
  - name: {slug}
    in: path
    required: true
    schema:
      type: string"""

    if args and method != "GET":
      docs += """
  - name: body
    in: body
    required: true
    schema:
      properties:"""

      for k, v in args.items():
          docs += f"""
          {k}:
            type: {decode_type(v)}
            description: ""
            required: {v.required}"""

          if v.default is not missing:
              docs += f"""
            default: {v.default}"""

    if args and method == "GET":
      for k, v in args.items():
        docs += f"""
  - name: {k}
    in: query
    required: {v.required}
    schema:
      type: {decode_type(v)}
      """

    return docs


def get_docs(route, url_prefix, method, _args=None, _auth="jwt"):
    route_attr = route_attrs.get(url_prefix)
    if route_attr:
      route_attr = route_attr.get(route)
    else:
      route_attr = build_route_attrs(route, url_prefix)

    if not route_attr:
        return """
To Be Updated
---
tags:
  - To Be Updated...
"""

    docs = """"""

    docs += f"""
{route_attr["title"]}"""

    if route_attr.get("description"):
        docs += f"""
{route_attr["description"]}"""

    docs +="""
---"""

    if route_attr.get("tags"):
        docs += f"""
tags:"""
        for tag in route_attr["tags"]:
            docs += f"""
  - {tag}"""

    docs += decode_webargs(route, method, _auth, _args)
    docs += f"""
{route_attr.get("responses")}
"""

    return docs

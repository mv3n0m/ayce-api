from .helpers import decode_type
from .constants import route_attrs
from webargs import missing


def decode_webargs(_auth="jwt", args=None):
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

    if args:
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

    return docs


def get_docs(route, _args=None, _auth="jwt"):
    route_attr = route_attrs.get(route)

    if not route_attr:
        return """
To Be Updated
---
tags:
  - Coming Soon...
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

    docs += decode_webargs(_auth, _args)
    docs += f"""
{route_attr.get("responses")}
"""

    return docs

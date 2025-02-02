# from .constants import swagger_types

swagger_types = {
    "string": "string",
    "email": "string",
    "date": "string",
    "datetime": "string",
    "integer": "integer",
    "float": "number",
    "list": "array",
    "dict": "object",
		"boolean": "boolean"
}

def decode_type(item):
	docs = """"""
	type_name = item.__class__.__name__.lower()
	docs += swagger_types.get(type_name)

	if type_name == "list":
		docs += f"""
            items:
              type: {decode_type(item.inner)}"""

	return docs

def build_response_docs(responses):
  docs = """
responses:"""

  for response in responses:
    _type = response["_type"]
    content = response.get("content")
    doc = f"""
  {response["status_code"]}:
    description: {response["description"]}
    content:
      application/json:
        schema:
          type: {_type}"""

    # if _type == "object":
    #   doc += """
    #       properties:"""
    #   for k, v in content.items():
    #     doc += f"""
    #         {k}:
    #           type: string
    #           description: {v}"""

    if _type == "array":
      doc += f"""
          items:
            type: {content}"""

    docs += doc

  return docs


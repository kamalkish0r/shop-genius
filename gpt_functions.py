import utils
import asyncio
import json

def get_products(query):
    products = asyncio.run(utils.scrape_products(query=query))
    return json.dumps(products, indent=4)

definitions = [
    {
        "name": "get_products",
        "description": "Gets products from the Amazon product database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gets the products based on the query"
                }
            }
        },
        "required": ["query"],
        "returns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "format": "string",
                        "description": "Product title"
                    },
                    "price": {
                        "type": "number",
                        "description": "Product price"
                    },
                    "MRP": {
                        "type": "number",
                        "description": "MRP of the product"
                    },
                    "availability": {
                        "type": "string",
                        "format": "string",
                        "description": "Availability of the product"
                    },
                    "rating": {
                        "type": "number",
                        "description": "Product rating"
                    },
                    "rating_count": {
                        "type": "number",
                        "description": "Number of ratings for the product"
                    },
                    "product_link": {
                        "type": "string",
                        "format": "uri",
                        "description": "Link to the product"
                    },
                    "Reviews": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "format": "string",
                                    "description": "Review title"
                                },
                                "review_rating": {
                                    "type": "string",
                                    "format": "string",
                                    "description": "Review rating"
                                },
                                "review": {
                                    "type": "string",
                                    "format": "string",
                                    "description": "Review text"
                                }
                            }
                        },
                        "description": "List of reviews for the product"
                    }
                }
            }
        }
    },
]

"""
Common function declarations.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import openai
import os
import qdrant_client as qc
import qdrant_client.http.models as models

DOC_TYPES = (
    "cheat_sheets", 
    "cli", 
    "environments", 
    "faq", 
    "getting_started", 
    "integrations", 
    "plugins",
    "recipes",
    "teams",
    "tutorials",
    "user_guide",
)

BLOCK_TYPES = (
    "code",
    "text",
)

MODEL = "text-embedding-ada-002"

CLIENT = qc.QdrantClient(url="localhost")
METRIC = models.Distance.DOT
DIMENSION = 1536

DEFAULT_COLLECTION_NAME = "fiftyone_docs"

HOME = os.path.expanduser("~")
FIFTYONE_DOCS_INDEX_FOLDER = os.path.join(HOME, ".fiftyone_docs_search")
FIFTYONE_DOCS_INDEX_FILENAME = "fiftyone_docs_index.json"
FIFTYONE_DOCS_INDEX_FILEPATH = os.path.join(
    FIFTYONE_DOCS_INDEX_FOLDER, 
    FIFTYONE_DOCS_INDEX_FILENAME
    )

BASE_DOCS_URL = "https://docs.voxel51.com/"

################################################################

def get_collection_name():
    collection_name = os.getenv("FIFTYONE_DOCS_COLLECTION")
    if collection_name is None or collection_name == "None":
        collection_name = DEFAULT_COLLECTION_NAME
    return collection_name

################################################################

def embed_text(text):
    response = openai.Embedding.create(
        input=text,
        model=MODEL
    )
    embeddings = response['data'][0]['embedding']
    return embeddings

################################################################

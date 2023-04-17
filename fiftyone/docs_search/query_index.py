"""
Index querying function declaration.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import os
import qdrant_client as qc
import qdrant_client.http.models as models
from rich import print
import webbrowser

from fiftyone.docs_search.create_index import download_index, load_index_from_json
from fiftyone.docs_search.common import *

################################################################

def parse_doc_types(doc_types):
    if doc_types is None:
        doc_types = DOC_TYPES
    elif type(doc_types) == str:
        doc_types = [doc_types]
    return doc_types

def parse_block_types(block_types):
    if block_types is None:
        block_types = BLOCK_TYPES
    elif type(block_types) == str:
        block_types = [block_types]
    return block_types


################################################################

def collection_exists(collection_name):
    collections = CLIENT.get_collections().collections
    collection_names = [collection.name for collection in collections]
    return collection_name in collection_names

def query_index(query, top_k=10, doc_types=None, block_types=None):
    collection_name = get_collection_name()

    if not collection_exists(collection_name):
        print(f"Collection {collection_name} does not exist. Creating...")
        if not os.path.exists(FIFTYONE_DOCS_INDEX_FILEPATH):
            print(f"Index JSON file {FIFTYONE_DOCS_INDEX_FILEPATH} does not exist.")
            download_index()
        load_index_from_json()


    vector = embed_text(query)

    _search_params = models.SearchParams(
        hnsw_ef=128,
        exact=False
    )

    doc_types = parse_doc_types(doc_types)
    block_types = parse_block_types(block_types)

    _filter = models.Filter(
        must=[
            models.Filter(
                should= [
                    models.FieldCondition(
                        key="doc_type",
                        match=models.MatchValue(value=dt),
                    )
                for dt in doc_types
                ],
        
            ),
            models.Filter(
                should= [
                    models.FieldCondition(
                        key="block_type",
                        match=models.MatchValue(value=bt),
                    )
                for bt in block_types
                ]  
            )
        ]
    )

    results = CLIENT.search(
        collection_name=collection_name,
        query_vector=vector,
        query_filter=_filter,
        limit=top_k,
        with_payload=True,
        search_params=_search_params,
    
    )

    results = [
        (
            f"{res.payload['url']}#{res.payload['section_anchor']}", 
            res.payload["text"],
            res.score
        )
        for res in results
    ]

    return results

################################################################

def add_breadcrumbs():
    fo_url = "https://github.com/voxel51/fiftyone"
    breadcrumb_string = ""
    breadcrumb_string += f"\u2B50 Star the FiftyOne repo! \u2B50 {fo_url} \u2B50\n"
    return  f"{breadcrumb_string : ^40}"

def format_string(s):
    s = s.replace("\(", "(").replace("\)", ")")
    return s

def print_results(query, results, score=True):
    print('\n'*3)
    print("="*80)
    str = f"Query: {query}"
    print(f"{str: ^80}")
    print("="*80)
    for i in range(len(results)):
        result = format_string(results[i][1])
        print(f"{i+1}) {results[i][0]}")
        print(f"--> {result}")
        if score:
            print(f"Score: {results[i][2]}")
        print("-"*80)
    print('\n'*2)
    print(add_breadcrumbs())

################################################################

def fiftyone_docs_search(
    query, 
    top_k=10, 
    doc_types=None, 
    block_types=None,
    score=False,
    open_url=True
):
    results = query_index(
        query,
        top_k=top_k,
        doc_types=doc_types,
        block_types=block_types
    )

    print_results(query, results, score=score)
    if open_url:
        top_url = results[0][0]
        webbrowser.open(top_url)

################################################################

class FiftyOneDocsSearch():
    """Class for handling FiftyOneDocsSearch queries."""
    def __init__(
            self, 
            top_k = None, 
            doc_types = None, 
            block_types = None, 
            score = False, 
            open_url = True
            ):
        self.default_top_k = top_k
        self.default_doc_types = doc_types
        self.default_block_types = block_types
        self.default_score = score
        self.default_open_url = open_url
        
    def __call__(
            self, 
            query, 
            top_k = None, 
            doc_types = None, 
            block_types = None, 
            score = None, 
            open_url = None
            ):
        args_dict = {}

        if top_k is None:
            top_k = self.default_top_k
        if top_k is not None:
            args_dict["top_k"] = top_k
        
        if doc_types is None:
            doc_types = self.default_doc_types
        if doc_types is not None:
            args_dict["doc_types"] = doc_types

        if block_types is None:
            block_types = self.default_block_types
        if block_types is not None:
            args_dict["block_types"] = block_types

        if score is None:
            score = self.default_score
        if score is not None:
            args_dict["score"] = score

        if open_url is None:
            open_url = self.default_open_url
        if open_url is not None:
            args_dict["open_url"] = open_url

        fiftyone_docs_search(query, **args_dict)

    
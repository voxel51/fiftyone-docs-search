"""
Index querying function declaration.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import qdrant_client as qc
import qdrant_client.http.models as qmodels
from rich import print
import webbrowser

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

def query_index(query, top_k=10, doc_types=None, block_types=None):
    collection_name = get_collection_name()

    vector = embed_text(query)

    _search_params = qmodels.SearchParams(
        hnsw_ef=128,
        exact=False
    )

    doc_types = parse_doc_types(doc_types)
    block_types = parse_block_types(block_types)

    _filter = qmodels.Filter(
        must=[
            qmodels.Filter(
                should= [
                    qmodels.FieldCondition(
                        key="doc_type",
                        match=qmodels.MatchValue(value=dt),
                    )
                for dt in doc_types
                ],
        
            ),
            qmodels.Filter(
                should= [
                    qmodels.FieldCondition(
                        key="block_type",
                        match=qmodels.MatchValue(value=bt),
                    )
                for bt in block_types
                ]  
            )
        ]
    )


        #     should= [
        #         qmodels.FieldCondition(
        #             key="doc_type",
        #             match=qmodels.MatchValue(value=dt),
        #         )
        #     for dt in doc_types
        #     ],
        #     should= [
        #         qmodels.FieldCondition(
        #             key="block_type",
        #             match=qmodels.MatchValue(value=bt),
        #         )
        #     for bt in block_types
        #     ]  
        # )

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
    print('\n'*3)

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
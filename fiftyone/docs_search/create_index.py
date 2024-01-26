"""
Index creating and loading function declarations.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from google.cloud import storage
import json
import os
import qdrant_client.http.models as models
import shutil
from tqdm import tqdm
import uuid

from fiftyone.docs_search.common import *
from fiftyone.docs_search.read_docs import (
    get_docs_list,
    get_markdown_documents,
)

################################################################


def generate_id():
    return str(uuid.uuid1().int)[:32]


def get_page_url(filepath):
    return f"{BASE_DOCS_URL}{filepath.split('html/')[1]}"


def get_doc_type(doc_path):
    for doc_type in DOC_TYPES:
        if doc_type in doc_path:
            return doc_type
    return None


################################################################


def initialize_index():
    collection_name = get_collection_name()

    CLIENT.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=DIMENSION,
            distance=METRIC,
        ),
    )


def add_vectors_to_index(ids, vectors, payloads):
    collection_name = get_collection_name()
    CLIENT.upsert(
        collection_name=collection_name,
        points=models.Batch(ids=ids, vectors=vectors, payloads=payloads),
    )


def create_subsection_vector(
    subsection_content,
    section_anchor,
    page_url,
    doc_type,
):

    vector = embed_text(subsection_content)
    id = generate_id()
    payload = {
        "text": subsection_content,
        "url": page_url,
        "section_anchor": section_anchor,
        "doc_type": doc_type,
    }
    return id, vector, payload


################################################################


def add_doc_to_index(filepath):
    subsections = get_markdown_documents(filepath)

    page_url = get_page_url(filepath)
    doc_type = get_doc_type(filepath)

    ids = []
    vectors = []
    payloads = []

    for section_anchor, section_content in subsections.items():
        if section_content == []:
            continue
        for subsection in section_content:
            id, vector, payload = create_subsection_vector(
                subsection,
                section_anchor,
                page_url,
                doc_type,
            )
            ids.append(id)
            vectors.append(vector)
            payloads.append(payload)

    add_vectors_to_index(ids, vectors, payloads)


################################################################


def generate_json_from_html_doc(doc):
    doc_json = {}
    sections = get_markdown_documents(doc)

    if len(sections) == 0:
        return
    if len(sections) == 1 and None in list(sections.keys()):
        return

    page_url = get_page_url(doc)
    doc_type = get_doc_type(doc)

    for section_anchor, section in sections.items():
        for subsection_content in section:
            if subsection_content == []:
                continue

            id, vector, payload = create_subsection_vector(
                subsection_content,
                section_anchor,
                page_url,
                doc_type,
            )
            doc_json[id] = {"vector": vector, **payload}

    return doc_json


def generate_json_from_html_docs(docs_index_file="fiftyone_docs_index.json"):
    docs_json = {}

    docs = get_docs_list()
    for doc in tqdm(docs):
        doc_json = generate_json_from_html_doc(doc)
        if doc_json is None:
            continue
        for id in doc_json:
            docs_json[id] = doc_json[id]

    with open(docs_index_file, "w") as f:
        json.dump(docs_json, f)


################################################################


def generate_index_from_html_docs():
    initialize_index()

    docs = get_docs_list()
    for doc in tqdm(docs):
        add_doc_to_index(doc)

    print("Index created successfully!")


################################################################


def save_index_to_json(
    docs_index_file="fiftyone_docs_index.json", batch_size=50
):
    collection_name = get_collection_name()
    collection = CLIENT.get_collection(collection_name=collection_name)
    num_vectors = collection.points_count
    docs_index = {}

    curr_points = CLIENT.scroll(
        collection_name=collection_name,
        limit=batch_size,
        with_payloads=True,
        with_vectors=True,
    )

    for i in tqdm(range(0, num_vectors, batch_size)):
        min_ind = i * batch_size

        curr_points = CLIENT.scroll(
            collection_name=collection_name,
            limit=10,
            offset=min_ind,
            with_payload=True,
            with_vectors=True,
        )[0]

        for point in curr_points:
            docs_index[point.id] = {"vector": point.vector, **point.payload}

    with open(docs_index_file, "w") as f:
        json.dump(docs_index, f)

    print(f"Index saved successfully to {docs_index_file}!")


################################################################


def load_index_from_json(docs_index_file=None, batch_size=500):

    initialize_index()
    tmp_index_file = (
        docs_index_file
        if docs_index_file is not None
        else FIFTYONE_DOCS_INDEX_FILENAME
    )
    shutil.copyfile(FIFTYONE_DOCS_INDEX_FILEPATH, tmp_index_file)
    with open(tmp_index_file, "r") as f:
        docs_index = json.load(f)
    os.remove(tmp_index_file)

    ids = []
    vectors = []
    payloads = []

    for id, value in docs_index.items():
        ids.append(id)
        vectors.append(value["vector"])

        payload_keys = (
            "text",
            "url",
            "section_anchor",
            "doc_type",
            "block_type",
        )
        payload = {key: value[key] for key in payload_keys}
        payloads.append(payload)

    for i in tqdm(range(0, len(ids), batch_size)):
        min_ind = i
        max_ind = min(i + batch_size, len(ids))

        curr_ids = ids[min_ind:max_ind]
        curr_vectors = vectors[min_ind:max_ind]
        curr_payloads = payloads[min_ind:max_ind]

        add_vectors_to_index(curr_ids, curr_vectors, curr_payloads)

    print("Index created successfully!")


################################################################


def download_index():
    print("Downloading index JSON from Google Drive...")
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket("fiftyone-docs-search")
    blob = bucket.blob("fiftyone_docs_index.json")

    tmp_file = FIFTYONE_DOCS_INDEX_FILENAME
    blob.download_to_filename(tmp_file)

    if not os.path.exists(FIFTYONE_DOCS_INDEX_FOLDER):
        os.mkdir(FIFTYONE_DOCS_INDEX_FOLDER)

    os.replace(tmp_file, FIFTYONE_DOCS_INDEX_FILEPATH)

# Search the FiftyOne Docs with an LLM

This repository contains the code to enable semantic search on the
[Voxel51 documentation](https://docs.voxel51.com) from Python or the command
line. The search is powered by [FiftyOne](https://github.com/voxel51/fiftyone),
OpenAI's [text-embedding-ada-002 model](https://platform.openai.com/docs/guides/embeddings), and [Qdrant vector search](https://qdrant.tech/).

!['fiftyone-docs-search-cli'](fiftyone/docs_search/images/cli_example.gif)

## Installation

1. Clone the repository:

```shell
git clone https://github.com/voxel51/fiftyone-docs-search
cd fiftyone-docs-search
```

2. Install the package:

```shell
pip install -e .
```

3. Register your OpenAI API key
   ([create one](https://platform.openai.com/account/api-keys)):

```shell
export OPENAI_API_KEY=XXXXXXXX
```

4. Launch a Qdrant server:

```shell
docker pull qdrant/qdrant
docker run -d -p 6333:6333 qdrant/qdrant
```

## Usage

### Command line

The `fiftyone-docs-search` package provides a command line interface for
searching the Voxel51 documentation. To use it, run:

```shell
fiftyone-docs-search query <query>
```

where `<query>` is the search query. For example:

```shell
fiftyone-docs-search query "how to load a dataset"
```

The following flags can give you control over the search behavior:

- `--num_results`: the number of results returned
- `--open_url`: whether to open the top result in your browser
- `--score`: whether to return the score of each result
- `--doc_types`: the types of docs to search over (e.g., "tutorials", "api", "guides")
- `--block_types`: the types of blocks to search over (e.g., "code", "text")

You can also use the `--help` flag to see all available options:

```shell
fiftyone-docs-search --help
```

#### Aliasing the command

If you find `fiftyone-docs-search query` cumbersome, you can alias the command, by adding the following to your `~/.bashrc` or `~/.zshrc` file:

```bash
alias fosearch='fiftyone-docs-search query'
```

### Python

!['fiftyone-docs-search-python'](fiftyone/docs_search/images/python_example.gif)

The `fiftyone-docs-search` package also provides a Python API for searching the
Voxel51 documentation. To use it, run:

```py
from fiftyone.docs_search import FiftyOneDocsSearch

fods = FiftyOneDocsSearch()
results = fods("how to load a dataset")
```

You can set defaults for the search behavior by passing arguments to the
constructor:

```py
fods = FiftyOneDocsSearch(
    num_results=5,
    open_url=True,
    score=True,
    doc_types=["tutorials", "api", "guides"],
    block_types=["code", "text"],
)
```

For any individual search, you can override these defaults by passing arguments.

## Versioning

The `fiftyone-docs-search` package is versioned to match the version of the
Voxel51 FiftyOne documentation that it is searching. For example, the `v0.20.1`
version of the `fiftyone-docs-search` package is designed to search the
`v0.20.1` version of the Voxel51 FiftyOne documentation.

## Building the index from scratch

By default, if you do not have a Qdrant collection instantiated yet, when you
run a search, the `fiftyone-docs-search` package will automatically download
a JSON file containing a vector indexing of the latest version of the Voxel51
FiftyOne documentation.

If you would like, you can also build the index yourself from a local copy of
the Voxel51 FiftyOne documentation. To do so, first clone the FiftyOne repo if
you haven't already:

```shell
git clone https://github.com/voxel51/fiftyone
```

and install FiftyOne, as described in the detailed installation instructions
[here](https://github.com/voxel51/fiftyone#installation-1).

Build a local version of the docs by running:

```shell
bash docs/generate_docs.bash
```

Then, set a `FIFTYONE_DIR` environment variable to the path to the local
FiftyOne repo. For example, if you cloned the repo to `~/fiftyone`, you would
run:

```shell
export FIFTYONE_DIR=~/fiftyone
```

Finally, run the following command to build the index:

```shell
fiftyone-docs-search create
```

If you would like to save the Qdrant index to JSON, you can run:

```shell
fiftyone-docs-search save -o <path to JSON file>
```

## Contributing

Contributions are welcome!

## About FiftyOne

If you've made it this far, we'd greatly appreciate if you'd take a moment to
check out [FiftyOne](https://github.com/voxel51/fiftyone) and give us a star!

FiftyOne is an open source library for building high-quality datasets and
computer vision models. It's the engine that powers this project.

Thanks for visiting! 😊

## Join the Community

If you want join a fast-growing community of engineers, researchers, and
practitioners who love computer vision, join the
[FiftyOne Slack community](https://slack.voxel51.com/)! 🚀🚀🚀

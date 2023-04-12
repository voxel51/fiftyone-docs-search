"""
Definition of the `fiftyone-docs-search` command-line interface (CLI).
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

import argparse
import argcomplete
import os


import fiftyone.docs_search.create_index as dsci
import fiftyone.docs_search.query_index as dsqi

################################################################

class Command(object):
    """Interface for defining commands.
    Command instances must implement the `setup()` method, and they should
    implement the `execute()` method if they perform any functionality beyond
    defining subparsers.
    """

    @staticmethod
    def setup(parser):
        """Setup the command-line arguments for the command.
        Args:
            parser: an `argparse.ArgumentParser` instance
        """
        raise NotImplementedError("subclass must implement setup()")

    @staticmethod
    def execute(parser, args):
        """Executes the command on the given args.
        args:
            parser: the `argparse.ArgumentParser` instance for the command
            args: an `argparse.Namespace` instance containing the arguments
                for the command
        """
        raise NotImplementedError("subclass must implement execute()")


class FiftyOneDocsSearchCommand(Command):
    """The FiftyOneDocsSearch command-line interface."""

    @staticmethod
    def setup(parser):
        subparsers = parser.add_subparsers(title="available commands")
        _register_command(subparsers, "create", CreateIndexCommand)
        _register_command(subparsers, "save", SaveIndexCommand)
        _register_command(subparsers, "load", LoadIndexCommand)
        _register_command(subparsers, "query", QueryIndexCommand)

    @staticmethod
    def execute(parser, args):
        parser.print_help()

class CreateIndexCommand(Command):
    """Creates the vector index for the docs.
    
    Examples::

        fiftyone-docs-search create --name my_name
    
    """

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-n",
            "--name",
            metavar="COLLECTION_NAME",
            default="fiftyone_docs",
            help="the name of the Qdrant collection to create",
        )

    @staticmethod
    def execute(parser, args):
        os.environ["FIFTYONE_DOCS_COLLECTION"] = str(args.collection_name)
        dsci.generate_index_from_html_docs()


class SaveIndexCommand(Command):
    """Saves the vector index for the docs.
    
    Examples::

        fiftyone-docs-search save -o my_index.json -b 100
    
    """

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-o",
            "--out_path",
            metavar="INDEX_JSON",
            default="fiftyone_docs_index.json",
            help="the name of the JSON file to save the index to",
        )

        parser.add_argument(
            "-b",
            "--batch_size",
            metavar="BATCH_SIZE",
            default=50,
            help="the pagination size for retrieving vectors from Qdrant index",
        )

    @staticmethod
    def execute(parser, args):
        dsci.save_index_to_json(
            docs_index_file = args.out_path, 
            batch_size = args.batch_size)


class LoadIndexCommand(Command):
    """Loads the vector index for the docs from JSON.
    
    Examples::

        fo-search load -i my_index.json
    
    """

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "-i",
            "--in_path",
            metavar="INDEX_JSON",
            default="fiftyone_docs_index.json",
            help="the name of the JSON file to load the index from",
        )

    @staticmethod
    def execute(parser, args):
        dsci.load_index_from_json(docs_index_file = args.in_path)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
class QueryIndexCommand(Command):
    """Queries the vector index for the docs.
    
    Examples::

        fiftyone-docs-search query "What is FiftyOne?" -n 10
    
    """

    @staticmethod
    def setup(parser):
        parser.add_argument(
            "query",
            metavar="QUERY",
            nargs="?",
            default="What is FiftyOne?",
            help="the query string to search for",
        )

        parser.add_argument(
            "-n",
            "--num_results",
            metavar="NUM_RESULTS",
            default=10,
            help="the number of results to return",
        )

        parser.add_argument(
            "-o",
            "--open_url",
            metavar="OPEN_URL",
            default=True,
            type=str2bool,
            help="whether to open the first result in a web browser",
        )

        parser.add_argument(
            "-s",
            "--score",
            metavar="SCORE",
            default=False,
            type=str2bool,
            help="whether to print the score of each result",
        )

        parser.add_argument(
            "-d",
            "--doc_types",
            metavar="DOC_TYPES",
            default=None,
            help="the types of docs to search through",
        )

        parser.add_argument(
            "-b",
            "--block_types",
            metavar="BLOCK_TYPES",
            default=None,
            help="the types of blocks to search through",
        )


    @staticmethod
    def execute(parser, args):
        dsqi.fiftyone_docs_search(
            args.query, 
            top_k = args.num_results,
            open_url = args.open_url,
            score = args.score,
            doc_types = args.doc_types,
            block_types = args.block_types
        )

        


def _has_subparsers(parser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return True

    return False


def _iter_subparsers(parser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for subparser in action.choices.values():
                yield subparser


class _RecursiveHelpAction(argparse._HelpAction):
    def __call__(self, parser, *args, **kwargs):
        self._recurse(parser)
        parser.exit()

    @staticmethod
    def _recurse(parser):
        print("\n%s\n%s" % ("*" * 79, parser.format_help()))
        for subparser in _iter_subparsers(parser):
            _RecursiveHelpAction._recurse(subparser)



def _register_main_command(command, version=None, recursive_help=True):
    parser = argparse.ArgumentParser(description=command.__doc__.rstrip())

    parser.set_defaults(execute=lambda args: command.execute(parser, args))
    command.setup(parser)

    if version:
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=version,
            help="show version info",
        )

    if recursive_help and _has_subparsers(parser):
        parser.add_argument(
            "--all-help",
            action=_RecursiveHelpAction,
            help="show help recursively and exit",
        )

    argcomplete.autocomplete(parser)
    return parser

def _register_command(parent, name, command, recursive_help=True):
    parser = parent.add_parser(
        name,
        help=command.__doc__.splitlines()[0],
        description=command.__doc__.rstrip(),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.set_defaults(execute=lambda args: command.execute(parser, args))
    command.setup(parser)

    if recursive_help and _has_subparsers(parser):
        parser.add_argument(
            "--all-help",
            action=_RecursiveHelpAction,
            help="show help recursively and exit",
        )

    return parser

__version__ = "0.20.1"

def main():
    """Executes the `fiftyone-docs-search` tool with the given command-line args."""
    parser = _register_main_command(
        FiftyOneDocsSearchCommand, 
        version="FiftyOneDocsSearch v%s" % __version__
        )
    args = parser.parse_args()
    args.execute(args)
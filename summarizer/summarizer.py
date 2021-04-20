# Created by bugra-yilmaz on 08.02.2021.
#
# Summarizer implementation to extract opinion-feature pairs from a review text

# Imports
import logging
from requests.exceptions import HTTPError

from nltk.parse.corenlp import CoreNLPServer
from nltk.parse.corenlp import CoreNLPServerError
from nltk.parse.corenlp import CoreNLPDependencyParser

# Define type aliases for review summarization
Remark = tuple[str, str]  # opinion-feature pair, example: ('nice', 'food')
Summary = list[Remark]  # list of remarks, i.e. opinion-feature pairs


class Summarizer:
    """
    Summarizer class implementing opinion-feature extraction. Uses Stanford CoreNLP dependency parser.

    Attributes:
    server (CoreNLPServer): CoreNLP server for accessing Stanford CoreNLP services.
    parser (CoreNLPDependencyParser): CoreNLP dependency parser.

    """
    def __init__(self, jar_path, models_jar_path):
        """
        The constructor for Summarizer class.

        Parameters:
        jar_path (str): Filepath to Stanford CoreNLP .jar file.
        models_jar_path (str): Filepath to Stanford CoreNLP models .jar file.

        """
        logging.info('Starting CoreNLP server...')
        self.server = CoreNLPServer(path_to_jar=jar_path, path_to_models_jar=models_jar_path)
        try:
            self.server.start()
            logging.info('CoreNLP server started.')
        # CoreNLPServerError is thrown when a server is already running
        except CoreNLPServerError:
            logging.warning('CoreNLP server is already running.')
        self.parser = CoreNLPDependencyParser()

    def summarize(self, text):
        """
        Summarizes a review. Extracts opinion-feature pairs from it.

        Parameters:
        text (str): Review text.

        Returns:
        Summary: List of opinion-feature pairs extracted from the review text.

        """
        try:
            parse = next(self.parser.raw_parse(text))
        # An HTTPError raised by the CoreNLP server is related to unrecognized characters in the review text
        except HTTPError:
            logging.warning(f'Review skipped: {text}')
            return []

        # Search dependency parsing result to find "nsubj" or "amod" tags
        summary = list()
        for governor, dep, dependent in parse.triples():
            if dep == 'nsubj':
                # Look if the nominal subject is noun and if it is modified by an adjective
                if governor[1] == 'JJ' and dependent[1] in {'NN', 'NNS'}:
                    summary.append((governor[0].lower(), dependent[0].lower()))
            elif dep == 'amod':
                # Look if the adjective is linked to a noun
                if dependent[1] == 'JJ' and governor[1] in {'NN', 'NNS'}:
                    summary.append((dependent[0].lower(), governor[0].lower()))
        return summary

    def stop(self):
        """
        Stops the CoreNLP server of the summarizer object.

        """
        self.server.stop()
        logging.info('CoreNLP server stopped.')

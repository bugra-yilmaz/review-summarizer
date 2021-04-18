import logging
from requests.exceptions import HTTPError

from nltk.parse.corenlp import CoreNLPServer
from nltk.parse.corenlp import CoreNLPServerError
from nltk.parse.corenlp import CoreNLPDependencyParser


class Summarizer:
    def __init__(self, jar_path, models_jar_path):
        logging.info('Starting CoreNLP server...')
        self.server = CoreNLPServer(path_to_jar=jar_path, path_to_models_jar=models_jar_path)
        try:
            self.server.start()
            logging.info('CoreNLP server started.')
        except CoreNLPServerError:
            logging.warning('CoreNLP server is already running.')
        self.parser = CoreNLPDependencyParser()

    def summarize(self, text):
        try:
            parse = next(self.parser.raw_parse(text))
        except HTTPError:
            logging.warning(f'Review skipped: {text}')
            return []

        summary = list()
        for governor, dep, dependent in parse.triples():
            if dep == 'nsubj':
                if governor[1] == 'JJ' and dependent[1] in {'NN', 'NNS'}:
                    summary.append((governor[0].lower(), dependent[0].lower()))
            elif dep == 'amod':
                if dependent[1] == 'JJ' and governor[1] in {'NN', 'NNS'}:
                    summary.append((dependent[0].lower(), governor[0].lower()))
        return summary

    def stop(self):
        self.server.stop()
        logging.info('CoreNLP server stopped.')

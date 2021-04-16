from nltk.parse.corenlp import CoreNLPServer
from nltk.parse.corenlp import CoreNLPDependencyParser


class Summarizer:
    def __init__(self, jar_path, models_jar_path):
        self.server = CoreNLPServer(path_to_jar=jar_path, path_to_models_jar=models_jar_path)
        self.server.start()
        self.parser = CoreNLPDependencyParser()

    def summarize(self, text):
        parse = next(self.parser.raw_parse(text))
        summary = list()
        for governor, dep, dependent in parse.triples():
            if dep == 'nsubj':
                if governor[1] == 'JJ' and dependent[1] == 'NN':
                    summary.append((governor[0].lower(), dependent[0].lower()))
            elif dep == 'amod':
                if dependent[1] == 'JJ' and governor[1] == 'NN':
                    summary.append((dependent[0].lower(), governor[0].lower()))
        return summary

    def stop(self):
        self.server.stop()

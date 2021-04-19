import re
import os
import time
import json
import logging
import argparse
from collections import Counter

from summarizer import Summarizer


def clean_review(text):
    return re.sub(r'[$%+^&@#*]+', r'', text)


def extract_reason(summaries, n_features=3):
    features = dict()
    for summary in summaries:
        for opinion, feature in summary:
            if feature in features:
                features[feature].append(opinion)
            else:
                features[feature] = [opinion]
    top_features = sorted(features.keys(), key=lambda x: len(features[x]), reverse=True)[:n_features]
    top_opinions = [Counter(features[feature]).most_common()[0][0] for feature in top_features]
    reason = [' '.join([opinion, feature]) for opinion, feature in zip(top_opinions, top_features)]
    return ','.join(reason)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-ybd', '--yelp-bus-data', help='Filepath to Yelp business dataset',
                                 dest='ybd', default='data/sample_business.json', metavar='')
    argument_parser.add_argument('-yrd', '--yelp-rew-data', help='Filepath to Yelp review dataset',
                                 dest='yrd', default='data/sample_review.json', metavar='')
    argument_parser.add_argument('-sj', '--stan-jar', help='Filepath to Stanford CoreNLP .jar file',
                                 dest='sj', default='data/stanford-corenlp-4.2.0.jar', metavar='')
    argument_parser.add_argument('-smj', '--stan-models-jar', help='Filepath to Stanford models .jar file',
                                 dest='smj', default='data/stanford-corenlp-4.2.0-models.jar', metavar='')
    argument_parser.add_argument('-n', '--n-restaurants', help='Number of restaurants to process',
                                 type=int, default=100, dest='n', metavar='')
    argument_parser.add_argument('-o', '--out', help='Filepath for saving the output file (in output directory)',
                                 default='restaurants.json', dest='o', metavar='')
    args = argument_parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)7s: %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

    logging.info('Collecting restaurants data...')
    t = time.time()
    restaurants = dict()
    with open(args.ybd, 'r') as f:
        for line in f:
            business = json.loads(line)
            if business['categories'] and 'Restaurants' in business['categories'].split(', '):
                restaurants[business['business_id']] = {'name': business['name'], 'rating': business['stars'],
                                                        'categories': business['categories'], 'reviews': set()}
                if len(restaurants) == args.n:
                    break
    logging.info(f'Collected {len(restaurants)} restaurants - {round(time.time() - t, 2)} seconds.')

    logging.info('Collecting and summarizing reviews data...')
    t = time.time()
    reviews = dict()
    summarizer = Summarizer(args.sj, args.smj)
    with open(args.yrd, 'r') as f:
        for line in f:
            review = json.loads(line)
            if review['business_id'] in restaurants:
                rating = review['stars']
                review_id, restaurant_id = review['review_id'], review['business_id']

                if rating > restaurants[restaurant_id]['rating']:
                    continue

                text = clean_review(review['text'])
                summary = summarizer.summarize(text)
                reviews[review_id] = {'rating': rating, 'summary': summary}
                restaurants[restaurant_id]['reviews'].add(review_id)

    summarizer.stop()
    logging.info(f'Collected and summarized {len(reviews)} reviews - {round(time.time() - t, 2)} seconds.')

    for restaurant, data in restaurants.items():
        summaries = list()
        for review_id in data['reviews']:
            summary = reviews[review_id]['summary']
            summaries.append(summary)
        reason = extract_reason(summaries)
        restaurants[restaurant]['reason'] = reason

    if not os.path.exists('output'):
        os.mkdir('output')
    with open(os.path.join('output', args.o), 'w') as f:
        for restaurant_id, data in restaurants.items():
            restaurant_object = {'business_id': restaurant_id, 'name': data['name'],
                                 'rating': data['rating'], 'reason': data['reason'],
                                 'categories': data['categories'].replace(' ', '')}
            f.write(f'{json.dumps(restaurant_object)}\n')

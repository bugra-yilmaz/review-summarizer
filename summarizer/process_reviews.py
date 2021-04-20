# Created by bugra-yilmaz on 08.02.2021.
#
# Review processing script to collecting reviews of each restaurant, summarizing them and storing the results

# Imports
import re
import os
import json
import logging
import argparse
from collections import Counter

from summarizer import Summary
from summarizer import Summarizer


def clean_review(text: str):
    """
    Removes a set of special characters from the review text for the sake of dependency parsing.

    Parameters:
    text (str): Review text.

    Returns:
    str: Cleaned review text.

    """
    return re.sub(r'[$%+^&@#*]+', r'', text)


def extract_reason(summaries: list[Summary], n_features: int = 3):
    """
    Extracts the reason from summarized review list.
    Returns the most frequent features and most frequent opinions about those features as seen in the review texts.

    Parameters:
    summaries (list[Summary]): List of summaries of review texts. Basically a list of opinion-feature pair lists.

    Returns:
    str: Reason string, constructed from most frequent feature and opinions. Example: "nice food, good service".

    """
    features = dict()
    # Collect opinions belonging to each feature
    for summary in summaries:
        for opinion, feature in summary:
            if feature in features:
                features[feature].append(opinion)
            else:
                features[feature] = [opinion]

    # Get n most frequent features of a restaurant
    top_features = sorted(features.keys(), key=lambda x: len(features[x]), reverse=True)[:n_features]
    # Get the most frequent opinion for each selected feature
    top_opinions = [Counter(features[feature]).most_common()[0][0] for feature in top_features]

    # Construct the reason with the most frequent features and corresponding opinions
    reason = [' '.join([opinion, feature]) for opinion, feature in zip(top_opinions, top_features)]

    return ','.join(reason)


if __name__ == '__main__':
    # Parse command line arguments
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

    # Format logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)7s: %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

    logging.info('Collecting restaurants data...')
    # Collect data for n restaurants from the given business data
    restaurants = dict()
    with open(args.ybd, 'r') as f:
        for line in f:
            business = json.loads(line)
            # Check if the business is a "Restaurant"
            if business['categories'] and 'Restaurants' in business['categories'].split(', '):
                restaurants[business['business_id']] = {'name': business['name'], 'rating': business['stars'],
                                                        'categories': business['categories'], 'reviews': set()}
                # Stop after collecting n restaurants
                if len(restaurants) == args.n:
                    break
    logging.info(f'Collected {len(restaurants)} restaurants.')

    logging.info('Collecting and summarizing reviews data...')
    # Collect review data belonging to already collected n restaurants
    reviews = dict()
    # Initialize the Stanford summarizer
    summarizer = Summarizer(args.sj, args.smj)
    with open(args.yrd, 'r') as f:
        for line in f:
            review = json.loads(line)

            # Do not collect reviews belonging to other businesses
            if review['business_id'] not in restaurants:
                continue

            rating = review['stars']
            review_id, restaurant_id = review['review_id'], review['business_id']

            # Consider only ratings with lower than or equal to average rating
            if rating > restaurants[restaurant_id]['rating']:
                continue

            # Clean the review text and summarize it - get opinion-feature pairs from it
            text = clean_review(review['text'])
            summary = summarizer.summarize(text)

            reviews[review_id] = {'rating': rating, 'summary': summary}
            restaurants[restaurant_id]['reviews'].add(review_id)

    # Stop the Stanford summarizer
    summarizer.stop()
    logging.info(f'Collected and summarized {len(reviews)} reviews.')

    # For each restaurant, collect summaries of reviews and extract the "reason"
    for restaurant, data in restaurants.items():
        summaries = list()
        for review_id in data['reviews']:
            summary = reviews[review_id]['summary']
            summaries.append(summary)
        # Get reason from collected summaries
        reason = extract_reason(summaries)
        restaurants[restaurant]['reason'] = reason

    # Write the output to a .json file with all the information needed in next steps
    if not os.path.exists('output'):
        os.mkdir('output')
    with open(os.path.join('output', args.o), 'w') as f:
        for restaurant_id, data in restaurants.items():
            restaurant_object = {'business_id': restaurant_id, 'name': data['name'],
                                 'rating': data['rating'], 'reason': data['reason'],
                                 'categories': data['categories'].replace(' ', '')}
            f.write(f'{json.dumps(restaurant_object)}\n')

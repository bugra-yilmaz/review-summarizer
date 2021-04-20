# Created by bugra-yilmaz on 08.02.2021.
#
# Unit test module for testing the REST API

# Imports
import unittest
import requests


class BasicTestCase(unittest.TestCase):
    # Test main URL for returned text
    def test_main_url(self):
        response = requests.get('http://localhost:5000')
        self.assertEqual(response.text, 'Welcome to the REST API!',
                         msg='Main url "/" does not return the expected placeholder text.')

    # Test the category parameter for case insensitivity
    def test_case_sensitivity(self):
        response_lower = requests.get('http://localhost:5000/restaurants?category=burgers')
        response_upper = requests.get('http://localhost:5000/restaurants?category=BURGERS')
        response_mixed = requests.get('http://localhost:5000/restaurants?category=bUrGERs')
        self.assertEqual(response_lower.json(), response_upper.json(),
                         msg='Case insensitivity is not satisfied for category search.')
        self.assertEqual(response_lower.json(), response_mixed.json(),
                         msg='Case insensitivity is not satisfied for category search.')

    # Test the response structure to see if it contains the needed fields
    def test_response_structure(self):
        response = requests.get('http://localhost:5000/restaurants?category=italian')
        key = 'restaurants'
        self.assertTrue(key in response.json(), msg=f'Response does not contain the key: {key}.')

        fields = ('business_id', 'name', 'rating', 'reason')
        fields_check = all(field in response.json()['restaurants'][0] for field in fields)
        self.assertTrue(fields_check, msg=f'Fields of a restaurant object are not: {fields}.')


# Run the unit tests
if __name__ == '__main__':
    unittest.main()

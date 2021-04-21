# Created by bugra-yilmaz on 08.02.2021.
#
# Unit test module for testing the REST API

# Imports
import unittest
import requests

# Define constant URL string
URL = 'http://localhost:5000'


class BasicTestCase(unittest.TestCase):
    # Test main endpoint for returned text
    def test_main_url(self):
        response = requests.get(URL)
        self.assertEqual(response.status_code, 200, msg='Status code is not OK for main endpoint.')
        self.assertEqual(response.text, 'Welcome to the REST API!',
                         msg='Main endpoint does not return the expected placeholder text.')

    # Test the restaurants endpoint for case insensitivity
    def test_case_sensitivity(self):
        response_lower = requests.get(URL + '/restaurants?category=burgers')
        response_upper = requests.get(URL + '/restaurants?category=BURGERS')
        response_mixed = requests.get(URL + '/restaurants?category=bUrGERs')
        self.assertEqual(response_lower.json(), response_upper.json(),
                         msg='Case insensitivity is not satisfied for category search.')
        self.assertEqual(response_lower.json(), response_mixed.json(),
                         msg='Case insensitivity is not satisfied for category search.')

    # Test the restaurants endpoint for response structure
    def test_response_structure(self):
        response = requests.get(URL + '/restaurants?category=italian')

        self.assertEqual(response.status_code, 200, msg='Status code is not OK for restaurants endpoint.')

        key = 'restaurants'
        self.assertTrue(key in response.json(), msg=f'Response does not contain the key: {key}.')

        fields = ('business_id', 'name', 'rating', 'reason')
        fields_check = all(field in response.json()['restaurants'][0] for field in fields)
        self.assertTrue(fields_check, msg=f'One or more required fields is missing in the restaurant object.')


# Run the unit tests
if __name__ == '__main__':
    unittest.main()

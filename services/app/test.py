import unittest
import requests


class BasicTestCase(unittest.TestCase):
    def test_main_url(self):
        response = requests.get('http://localhost:5000')
        self.assertEqual(response.text, 'Welcome to the REST API!',
                         msg='Main url "/" does not return the expected placeholder text.')

    def test_case_sensitivity(self):
        response_lower = requests.get('http://localhost:5000/restaurants?category=burgers')
        response_upper = requests.get('http://localhost:5000/restaurants?category=BURGERS')
        response_mixed = requests.get('http://localhost:5000/restaurants?category=bUrGERs')
        self.assertEqual(response_lower.json(), response_upper.json(),
                         msg='Case insensitivity is not satisfied for category search.')
        self.assertEqual(response_lower.json(), response_mixed.json(),
                         msg='Case insensitivity is not satisfied for category search.')

    def test_response_structure(self):
        response = requests.get('http://localhost:5000/restaurants?category=italian')
        key = 'restaurants'
        self.assertTrue(key in response.json(), msg=f'Response does not contain the key: {key}.')

        fields = ('business_id', 'name', 'rating', 'reason')
        fields_check = all(field in response.json()['restaurants'][0] for field in fields)
        self.assertTrue(fields_check, msg=f'Fields of a restaurant object are not: {fields}.')


if __name__ == '__main__':
    unittest.main()

"""Module with all tests for the orderStep class"""


import unittest
from app.models import Database, User, orderCategory, \
order, orderStep
from app import utilities

class orderStepTest(unittest.TestCase):
    """All tests for the orderStep class"""
    
    def setUp(self):
        """Initiates variables to be used in most tests"""
        self.db = Database()
        self.user_data = {
            'key': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password',
            }
        self.user = User(**self.user_data)
        self.db = Database()
        self.user.save(self.db)
        self.category_data = {
            'key': 1,
            'name': 'cakes',
            'description': 'all orders cake!',
            'user': self.user.key,
        }
        self.category = orderCategory(**self.category_data)
        self.category.save(self.db)
        self.order_data = {
            'key': 1,
            'name': 'Banana cake',
            'description': 'yummy!',
            'category': self.category.key
        }
        self.order = order(**self.order_data)
        self.order.save(self.db)
        self.order_step_data = {
            'key': 1,
            'text_content': "Don't do anything",
            'order': self.order.key
        }
        self.order_step = orderStep(**self.order_step_data)

    def test_text_content_is_mandatory(self):
        """
        In the constructor, the text_content parameter should be 
        a string which is not empty
        """
        self.assertRaises(TypeError, orderStep, key=1,order=self.order.key)
        invalid_data = utilities.replace_value_in_dict(self.order_step_data,
                                                       'text_content', 7)
        self.assertRaises(TypeError, orderStep, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.order_step_data,
                                                       'text_content', '')
        self.assertRaises(ValueError, orderStep, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.order_step_data,
                                                       'text_content', '  ')
        self.assertRaises(ValueError, orderStep, **invalid_data)

    def test_save_method(self):
        """
        The save() method should be able to update the parent order's 
        list of order_steps as well as that of the database
        """
        self.assertIsInstance(self.order_step, orderStep)
        self.order_step.save(self.db)
        length_of_db_order_step_keys = len(self.db.order_step_keys)
        length_of_order_steps = len(self.order.order_steps)
        self.assertIn(self.order_step.key, self.db.order_step_keys)
        self.assertEqual(self.order_step, self.db.order_steps[self.order_step.key])
        self.assertIn(self.order_step.key, self.order.order_steps)
        # the order should exist in database
        invalid_data = utilities.replace_value_in_dict(self.order_step_data, 'order', 78)
        new_order_step = orderStep(**invalid_data)
        self.assertRaises(KeyError, new_order_step.save, self.db)
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.order_step.save, 
                          'string instead of Database object')
        # calling save more than once does not increase size of self.db.order_step_keys
        self.order_step.save(self.db)
        self.assertEqual(len(self.db.order_step_keys), length_of_db_order_step_keys)
        # calling save more than once does not increase size of self.order.order_steps
        self.assertEqual(len(self.order.order_steps), length_of_order_steps)

    def test_delete(self):
        """orderStep object can be deleted"""
        self.assertIsInstance(self.order_step, orderStep)
        self.order_step.save(self.db)
        self.assertEqual(self.order_step, self.db.order_steps[self.order_step.key])
        self.assertEqual(self.order_step, self.db.order_steps.get(self.order_step.key))
        self.order_step.delete(self.db)
        self.assertRaises(KeyError, utilities.return_value_from_dict,
                          self.db.order_steps, self.order_step.key)
        self.assertNotIn(self.order_step.key, self.db.order_step_keys)
        self.assertNotIn(self.order_step.key, self.order.order_steps)
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.order_step.delete, 
                          'string instead of Database object')
        # calling delete more than once on same Database object raises KeyError
        self.assertRaises(KeyError, self.order_step.delete, self.db)

    def test_set_text_content(self):
        """ The text_content can be set with a new non-empty string value"""
        # try to set a new name
        new_text = 'Do this instead'
        # save to db
        self.order_step.save(self.db)
        self.order_step.set_text_content(new_text, self.db)
        # the records in db should be updated also
        self.assertEqual(self.order_step, self.db.order_steps[self.order_step.key])
        self.assertIn(self.order_step.key, self.db.order_step_keys)
        # assert that the new text content is set
        self.assertEqual(new_text, self.order_step.text_content)
        # try setting with a non string name
        self.assertRaises(TypeError, self.order_step.set_text_content, 2, self.db)
        # try setting with an empty string
        self.assertRaises(ValueError, self.order_step.set_text_content, '', self.db)
        # try setting with a space string 
        self.assertRaises(ValueError, self.order_step.set_text_content, '  ', self.db)
        # try setting with a database that is not a Database
        self.assertRaises(TypeError, self.order_step.set_text_content, 'blah blah blah',
                          'a string instead of database')


if __name__ == '__main__':
    unittest.main()
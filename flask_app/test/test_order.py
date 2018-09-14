"""Module containing all the tests for order class"""


import unittest
from app.models import Database, User, orderCategory,\
order, orderStep
from app import utilities


class orderTest(unittest.TestCase):
    """All tests for the order class"""
    
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
            'name': 'Chicken – Combo',
            'description': '2 Pc. Chicken – Combo-20,000Ugshs',
            'user': self.user.key,
        }
        self.category = orderCategory(**self.category_data)
        self.category.save(self.db)
        self.order_data = {
            'key': 1,
            'name': 'Roast Pork',
            'description': 'Roast Pork-30,000Ugshs',
            'category': self.category.key
        }
        self.order = order(**self.order_data)
        self.order_step_data = {
            'text_content': "Waiting for your order ....",
        }

    def test_name_is_mandatory(self):
        """
        In the constructor, the name parameter should be 
        a string which is not empty
        """
        self.assertRaises(TypeError, order, key=1,
                          description='', category=self.category.key)
        invalid_data = utilities.replace_value_in_dict(self.order_data, 'name', 7)
        self.assertRaises(TypeError, order, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.order_data, 'name', '')
        self.assertRaises(ValueError, order, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.order_data, 'name', ' ')
        self.assertRaises(ValueError, order, **invalid_data)

    def test_save_method(self):
        """
        The save() method should be able to update the parent category's 
        list of orders as well as that of the database
        """
        self.assertIsInstance(self.order, order)
        self.order.save(self.db)
        length_of_db_order_keys = len(self.db.order_keys)
        length_of_category_orders = len(self.category.orders)
        self.assertIn(self.order.key, self.db.order_keys)
        self.assertEqual(self.order, self.db.orders[self.order.key])
        self.assertIn(self.order.key, self.category.orders)
        self.assertIn(self.order.name, self.db.order_name_key_map.keys())
        self.assertEqual(self.order.key,
                         self.db.order_name_key_map[self.order.name])
        # the category should exist in database
        invalid_data = utilities.replace_value_in_dict(self.order_data, 'category', 78)
        new_order = order(**invalid_data)
        self.assertRaises(KeyError, new_order.save, self.db)
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.order.save, 
                          'string instead of Database object')
        # calling save more than once does not increase size of self.db.order_keys
        self.order.save(self.db)
        self.assertEqual(len(self.db.order_keys), length_of_db_order_keys)
        # calling save more than once does not increase size of self.category.orders
        self.assertEqual(len(self.category.orders), length_of_category_orders)

    def test_delete(self):
        """order can be deleted"""
        self.assertIsInstance(self.order, order)
        self.order.save(self.db)
        self.assertEqual(self.order, self.db.orders[self.order.key])
        self.assertEqual(self.order, self.db.orders.get(self.order.key))
        self.order.delete(self.db)
        self.assertRaises(KeyError, utilities.return_value_from_dict,
                          self.db.orders, self.order.key)
        self.assertNotIn(self.order.key, self.db.order_keys)
        self.assertNotIn(self.order.key, self.category.orders)
        self.assertNotIn(self.order.name, self.db.order_name_key_map.keys())
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.order.delete, 
                          'string instead of Database object')
        # calling delete more than once on same Database objec raises KeyError
        self.assertRaises(KeyError, self.order.delete, self.db)

    def test_set_name(self):
        """ The name can be set with a new non-empty string value"""
        # try to set a new name
        new_name = 'foo'
        # save to db
        self.order.save(self.db)
        self.order.set_name(new_name, self.db)
        # the records in db should be updated also
        self.assertEqual(self.order, self.db.orders[self.order.key])
        self.assertIn(self.order.key, self.db.order_keys)
        self.assertIn(self.order.name, self.db.order_name_key_map.keys())
        self.assertEqual(self.order.key, self.db.order_name_key_map[self.order.name])
        # assert that the new name is set
        self.assertEqual(new_name, self.order.name)
        # try setting with a non string name
        self.assertRaises(TypeError, self.order.set_name, 2, self.db)
        # try setting with an empty string
        self.assertRaises(ValueError, self.order.set_name, '', self.db)
        # try setting with a space string 
        self.assertRaises(ValueError, self.order.set_name, '  ', self.db)
        # try setting with a database that is not a Databas
        self.assertRaises(TypeError, self.order.set_name, 'new name',
                          'a string instead of database')

    def test_set_description(self):
        """ The description can be set with a new non-empty string value"""
        # try to set a new description
        new_description = 'bar'
        # Save to self.db
        self.order.save(self.db)
        self.order.set_description(new_description, self.db)
        self.assertEqual(self.order, self.db.orders[self.order.key])
        self.assertIn(self.order.key, self.db.order_keys)
        self.assertIn(self.order.name, self.db.order_name_key_map.keys())
        self.assertEqual(self.order.key, self.db.order_name_key_map[self.order.name])
        # assert that the new description is set
        self.assertEqual(new_description, self.order.description)
        # try setting with a non string description
        self.assertRaises(TypeError, self.order.set_description, 2, self.db)
        # the records in db should be updated also
        # try setting with a database that is not a Databas
        self.assertRaises(TypeError, self.order.set_description, 'new description',
                          'a string instead of database')

    def test_order_can_create_steps(self):
        """order can create steps under it"""
        self.order.save(self.db)
        order_step = self.order.create_step(self.db, self.order_step_data)
        self.assertIsInstance(order_step, orderStep)
        self.assertIn(order_step.key, self.order.order_steps)
        self.assertIn(order_step.key, self.db.order_step_keys)
        self.assertEqual(order_step, self.db.order_steps[order_step.key])
        self.assertRaises(TypeError, self.order.create_step, 
                          'database should be a Database object', self.order_step_data)
        del(self.order_step_data['text_content'])
        order_step = self.order.create_step(self.db, self.order_step_data)
        self.assertIsNone(order_step)

    def test_get_all_steps(self):
        """The get_all_steps function should be able to retrieve all steps"""
        text_content_tuple = ('Chicken', 'Pizza', 'Mushroom Soup')
        # create three order steps
        created_order_steps = []
        # incase an order step is ever created in the Setup
        key = 2
        # save order in db
        self.order.save(self.db)
        for text_content in text_content_tuple:
            new_data = utilities.replace_value_in_dict(self.order_step_data,
                                                       'text_content', text_content)
            new_order_step = orderStep(**new_data, key=key, order=self.order.key)
            new_order_step.save(self.db)
            created_order_steps.append(new_order_step)
            key += 1

        order_steps = self.order.get_all_steps(self.db)
        self.assertIsInstance(order_steps, list)
        self.assertEqual(len(self.order.order_steps), len(order_steps))
        self.assertListEqual(created_order_steps, order_steps)
        self.assertRaises(TypeError, self.order.get_all_steps,
                          'expected Database object not string')


if __name__ == '__main__':
    unittest.main()
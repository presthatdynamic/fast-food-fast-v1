"""
This includes the tests for the User Object
"""

import unittest
from app.models import Database, User, order, orderCategory, \
orderStep
from app import utilities

class DatabaseTest(unittest.TestCase):
    """
    Tests for the Database class
    """

    def setUp(self):
        """Declares variables to be used in most tests"""
        self.db = Database()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password',
            }
        self.user = User(**self.user_data, key=1)
        self.category_data = {
            'key': 1,
            'name': 'cakes',
            'description': 'all orders cake!',
            'user': self.user.key,
        }
        self.order_data = {
            'key': 1,
            'name': 'breadcake',
            'description': 'yummy',
            'category': self.category_data['key'],
        }
        self.order_step_data = {
            'key': 1,
            'text_content': "Don't do anything",
            'order': self.order_data['key'],
        }

    def test_get_next_key(self):
        """The next key for each model object type can be got"""
        self.assertEqual(self.db.get_next_key(User), 1)
        self.assertEqual(self.db.get_next_key(order), 1)
        self.assertEqual(self.db.get_next_key(orderCategory), 1)
        self.assertEqual(self.db.get_next_key(orderStep), 1)
        self.db._user_keys += [1,2,3]
        self.assertEqual(self.db.get_next_key(User), 4)
        self.db._order_keys += [1,2,3,7]
        self.assertEqual(self.db.get_next_key(order), 8)
        self.db._order_category_keys += [1,2,3, 4]
        self.assertEqual(self.db.get_next_key(orderCategory), 5)
        self.db._order_step_keys += [1,2,3,9]
        self.assertEqual(self.db.get_next_key(orderStep), 10)
        self.assertRaises(TypeError, self.db.get_next_key, 2)

    def test_create_user(self):
        """A user can be created in 'Database'"""
        user = self.db.create_user(self.user_data)
        self.assertIsInstance(user, User)
        self.assertIn(user.key, self.db.user_keys)
        self.assertEqual(user, self.db.users[user.key])
        self.assertIn(user.email, self.db.user_email_key_map.keys())
        self.assertEqual(user.key, self.db.user_email_key_map[user.email])

    def test_get_user(self):
        """A user can be got by user_key"""
        user = User(**self.user_data, key=1)
        user.save(self.db)
        user_from_db = self.db.get_user(user.key)
        self.assertEqual(user, user_from_db)
        non_existent_key = 3
        self.assertIsNone(self.db.get_user(non_existent_key))
        self.assertRaises(TypeError, self.db.get_user, 'user_key should be int')

    def test_get_user_by_email(self):
        """A user can be got by email"""
        user = self.db.create_user(self.user_data)
        self.assertIsInstance(user, User)
        user_instance = self.db.get_user_by_email(user.email)
        self.assertEqual(user, user_instance)
        self.assertRaises(TypeError, self.db.get_user_by_email, 2)

    def test_get_order_category(self):
        """A order category can be retrieved by key"""
        # setup
        self.user.save(self.db)
        # create category
        category = orderCategory(**self.category_data)
        # save category
        category.save(self.db)
        # try retrieving the category
        category_from_db = self.db.get_order_category(category.key)
        self.assertEqual(category, category_from_db)
        # try retrieving a non-existent category
        self.assertIsNone(self.db.get_order_category(4))
        # try using a non-int key
        self.assertRaises(TypeError, self.db.get_order_category, 'string instead of int')

    def test_delete_object_for_category(self):
        """delete_object should be able to remove the object passed to it from the database"""
        # setup
        self.user.save(self.db)
        # create category
        category = orderCategory(**self.category_data)
        # save category
        category.save(self.db)
        # create order
        order = order(**self.order_data)
        # save order as child of category due to key set in setUp
        order.save(self.db)
        # delete category
        ##################Test deleting categories####################
        self.db.delete_object(category)
        # assert that the category object is not in self.db.order_categories
        self.assertRaises(KeyError, utilities.return_value_from_dict, self.db.order_categories, category.key)
        # assert that the order object is not in self.db.orders
        self.assertRaises(KeyError, utilities.return_value_from_dict, self.db.orders, order.key)
        # assert that the category key is not in self.db.order_category_keys
        self.assertNotIn(category.key, self.db.order_category_keys)
        # assert that the order key is not in self.db.order_keys
        self.assertNotIn(order.key, self.db.order_keys)
        # assert that the category name is not in self.db.order_categories_name_key_map
        self.assertNotIn(category.name, self.db.order_category_name_key_map.keys())
        # assert that the order name is not in self.db.order_name_key_map
        self.assertNotIn(order.name, self.db.order_name_key_map.keys())
        # try to delete a non existent object by deleting category again
        self.assertRaises(KeyError, self.db.delete_object, category)
        # try to delete an object of a type that does not exist in database
        self.assertRaises(TypeError, self.db.delete_object, 2)

    def test_delete_object_for_orders(self):
        """delete_object should be able to remove the object passed to it from the database"""
        # setup
        self.user.save(self.db)
        category = orderCategory(**self.category_data)
        category.save(self.db)
        order = order(**self.order_data)
        order.save(self.db)
        # create step as child of order
        order_step = orderStep(**self.order_step_data)
        order_step.save(self.db)
        # delete order
        self.db.delete_object(order)
        # assert that the order step object is not in self.db.order_steps
        self.assertRaises(KeyError, utilities.return_value_from_dict, self.db.order_steps, order_step.key)
        # assert that the order object is not in self.db.orders
        self.assertRaises(KeyError, utilities.return_value_from_dict, self.db.orders, order.key)
        # assert that the order step key is not in self.db.order_step_keys
        self.assertNotIn(order_step.key, self.db.order_step_keys)
        # assert that the order key is not in self.db.order_keys
        self.assertNotIn(order.key, self.db.order_keys)
        # assert that the order name is not in self.db.order_name_key_map
        self.assertNotIn(order.name, self.db.order_name_key_map.keys())
        # try to delete a non existent object by deleting category again
        self.assertRaises(KeyError, self.db.delete_object, order)

    def test_get_order(self):
        """A order can be retrieved by key"""
        # setup
        self.user.save(self.db)
        category = orderCategory(**self.category_data)
        category.save(self.db)
        order = order(**self.order_data)
        order.save(self.db)
        # try retrieving the order
        order_from_db = self.db.get_order(order.key)
        self.assertEqual(order, order_from_db)
        # try retrieving a non-existent order
        self.assertIsNone(self.db.get_order(4))
        # try using a non-int key
        self.assertRaises(TypeError, self.db.get_order, 'string instead of int')

    def test_get_order_step(self):
        """A order step can be retrieved by key"""
        # setup
        self.user.save(self.db)
        category = orderCategory(**self.category_data)
        category.save(self.db)
        order = order(**self.order_data)
        order.save(self.db)
        order_step = orderStep(**self.order_step_data)
        order_step.save(self.db)
        # try retrieving the order step
        order_step_from_db = self.db.get_order_step(order_step.key)
        self.assertEqual(order_step, order_step_from_db)
        # try retrieving a non-existent order step
        self.assertIsNone(self.db.get_order_step(50))
        # try using a non-int key
        self.assertRaises(TypeError, self.db.get_order_step, 'string instead of int')


        



    # key should not be negative or zero
    # key should not exist already


if __name__ == '__main__':
    unittest.main()
    
"""Module holds tests for the orderCategory class"""


import unittest
from app.models import Database, User, orderCategory, order
from app import utilities


class orderCategoryTest(unittest.TestCase):
    """All tests for the orderCategory class"""
    
    def setUp(self):
        """Initiates variables to be used in most tests"""
        self.db = Database()
        self.user_data = {
            'key': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'preston@example.com',
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
        self.order_data = {
            'name': 'Banana cake',
            'description': 'yummy!',
        }

    def test_name_is_mandatory(self):
        """
        In the constructor, the name parameter should be 
        a string which is not empty
        """
        self.assertRaises(TypeError, orderCategory, key=1,
                          description='', user=self.user.key)
        invalid_data = utilities.replace_value_in_dict(self.category_data, 'name', 7)
        self.assertRaises(TypeError, orderCategory, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.category_data, 'name', '')
        self.assertRaises(ValueError, orderCategory, **invalid_data)
        invalid_data = utilities.replace_value_in_dict(self.category_data, 'name', ' ')
        self.assertRaises(ValueError, orderCategory, **invalid_data)

    def test_save_method(self):
        """
        The save() method should be able to update the parent user's 
        list of order categories as well as that of the database
        """
        self.assertIsInstance(self.category, orderCategory)
        self.category.save(self.db)
        length_of_db_category_keys = len(self.db.order_category_keys)
        length_of_user_categories = len(self.user.order_categories)
        self.assertIn(self.category.key, self.db.order_category_keys)
        self.assertEqual(self.category, self.db.order_categories[self.category.key])
        self.assertIn(self.category.key, self.user.order_categories)
        self.assertIn(self.category.name, self.db.order_category_name_key_map.keys())
        self.assertEqual(self.category.key,
                         self.db.order_category_name_key_map[self.category.name])
        # the user should exist in database
        invalid_data = utilities.replace_value_in_dict(self.category_data, 'user', 78)
        new_category = orderCategory(**invalid_data)
        self.assertRaises(KeyError, new_category.save, self.db)
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.category.save, 
                          'string instead of Database object')
        # calling save more than once does not increase size of self.db.order_category_keys
        self.category.save(self.db)
        self.assertEqual(len(self.db.order_category_keys), length_of_db_category_keys)
        # calling save more than once does not increase size of self.user.order_categories
        self.assertEqual(len(self.user.order_categories), length_of_user_categories)

    def test_delete(self):
        """orderCategory can be deleted"""
        self.assertIsInstance(self.category, orderCategory)
        self.category.save(self.db)
        self.assertEqual(self.category, self.db.order_categories[self.category.key])
        self.assertEqual(self.category, self.db.order_categories.get(self.category.key))
        self.category.delete(self.db)
        self.assertRaises(KeyError, utilities.return_value_from_dict,
                          self.db.order_categories, self.category.key)
        self.assertNotIn(self.category.key, self.db.order_category_keys)
        self.assertNotIn(self.category.key, self.user.order_categories)
        self.assertNotIn(self.category.name, self.db.order_category_name_key_map.keys())
        # database parameter should be of type Database
        self.assertRaises(TypeError, self.category.delete, 
                          'string instead of Database object')
        # calling delete more than once on same Database objec raises KeyError
        self.assertRaises(KeyError, self.category.delete, self.db)

    def test_set_name(self):
        """ The name can be set with a new non-empty string value"""
        # try to set a new name
        new_name = 'foo'
        # save to db
        self.category.save(self.db)
        self.category.set_name(new_name, self.db)
        # the records in db should be updated also
        self.assertEqual(self.category, self.db.order_categories[self.category.key])
        self.assertIn(self.category.key, self.db.order_category_keys)
        self.assertIn(self.category.name, self.db.order_category_name_key_map.keys())
        self.assertEqual(self.category.key, self.db.order_category_name_key_map[self.category.name])
        # assert that the new name is set
        self.assertEqual(new_name, self.category.name)
        # try setting with a non string name
        self.assertRaises(TypeError, self.category.set_name, 2, self.db)
        # try setting with an empty string
        self.assertRaises(ValueError, self.category.set_name, '', self.db)
        # try setting with a space string 
        self.assertRaises(ValueError, self.category.set_name, '  ', self.db)
        # try setting with a database that is not a Databas
        self.assertRaises(TypeError, self.category.set_name, 'new name',
                          'a string instead of database')
    
    def test_set_description(self):
        """ The description can be set with a new non-empty string value"""
        # try to set a new description
        new_description = 'bar'
        # Save to self.db
        self.category.save(self.db)
        self.category.set_description(new_description, self.db)
        self.assertEqual(self.category, self.db.order_categories[self.category.key])
        self.assertIn(self.category.key, self.db.order_category_keys)
        self.assertIn(self.category.name, self.db.order_category_name_key_map.keys())
        self.assertEqual(self.category.key, self.db.order_category_name_key_map[self.category.name])
        # assert that the new description is set
        self.assertEqual(new_description, self.category.description)
        # try setting with a non string description
        self.assertRaises(TypeError, self.category.set_description, 2, self.db)
        # the records in db should be updated also
        # try setting with a database that is not a Databas
        self.assertRaises(TypeError, self.category.set_description, 'new description',
                          'a string instead of database')

    def test_category_can_create_orders(self):
        """Category can create orders under it"""
        order = self.category.create_order(self.db, self.order_data)
        self.assertIsInstance(order, order)
        self.assertIn(order.key, self.category.orders)
        self.assertIn(order.key, self.db.order_keys)
        self.assertEqual(order, self.db.orders[order.key])
        self.assertIn(order.name, self.db.order_name_key_map.keys())
        self.assertEqual(order.key,
                          self.db.order_name_key_map[order.name])
        self.assertRaises(TypeError, self.category.create_order, 
                          'database should be a Database object', self.order_data)
        del(self.order_data['name'])
        order = self.category.create_order(self.db, self.order_data)
        self.assertIsNone(order)

    def test_get_all_orders(self):
        """The get_all_orders function should be able to retrieve all orders"""
        names = ('Banana cake', 'fruit cake', 'icy cake')
        # create three orders
        created_orders = []
        # incase a order is ever created in the Setup
        key = 2
        # save category in db
        self.category.save(self.db)
        for name in names:
            new_data = utilities.replace_value_in_dict(self.order_data, 'name', name)
            new_order = order(**new_data, key=key, category=self.category.key)
            new_order.save(self.db)
            created_orders.append(new_order)
            key += 1

        orders = self.category.get_all_orders(self.db)
        self.assertIsInstance(orders, list)
        self.assertEqual(len(self.category.orders), len(orders))
        self.assertListEqual(created_orders, orders)
        self.assertRaises(TypeError, self.category.get_all_orders,
                          'expected Database object not string')


if __name__ == '__main__':
    unittest.main()


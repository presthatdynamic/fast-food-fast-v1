"""
This module holds the pretend-models for the application
"""
from random import randint
from app.utilities import check_type, check_email_format

def binary_search(character, list_of_characters, position=0):
    """
    Searches for character using binary search
    returns None if character is not found
    otherwise returns character's position in sorted list
    """
    length_of_list = len(list_of_characters)
    if length_of_list <= 1:
        if length_of_list == 0:
            return None
        if character != list_of_characters[0]:
            return None
        return position

    random_int = randint(0, length_of_list - 1)
    if character < list_of_characters[random_int]:
        new_list = list_of_characters[:(random_int)]
        position += 0
    else:
        new_list = list_of_characters[random_int:]
        position += random_int
    # return this so that it recursively comes back to the surface
    return binary_search(character, new_list, position)


class Database:
    """This is the daabase for the application"""
    def __init__(self):
        self.users = {}
        self.orders = {}
        self.order_categories = {}
        self.order_steps = {}
        self._user_keys = []
        self.user_email_key_map = {}
        self._order_keys = []
        self.order_name_key_map = {}
        self._order_category_keys = []
        self.order_category_name_key_map = {}
        self._order_step_keys = []

    @property
    def order_category_keys(self):
        self._order_category_keys =  list(set(self._order_category_keys))
        return self._order_category_keys

    @property
    def order_keys(self):
        self._order_keys =  list(set(self._order_keys))
        return self._order_keys

    @property
    def order_step_keys(self):
        self._order_step_keys =  list(set(self._order_step_keys))
        return self._order_step_keys

    @property
    def user_keys(self):
        self._user_keys =  list(set(self._user_keys))
        return self._user_keys

    def get_next_key(self, type_of_object):
        """Gets the next key basing on the type of object"""
        # type_of_object should be of type type
        if check_type(type_of_object, type):
            if type_of_object == User:
                return self.__get_max_value(self.user_keys) + 1

            if type_of_object == order:
                return self.__get_max_value(self.order_keys) + 1

            if type_of_object == orderCategory:
                return self.__get_max_value(self.order_category_keys) + 1

            if type_of_object == orderStep:
                return self.__get_max_value(self.order_step_keys) + 1

    def __get_max_value(self, unsorted_list):
        """Returns the maximum value of a list or 0 if list is empty"""
        if check_type(unsorted_list, list):
            length = len(unsorted_list)
            if length == 0:
                return 0

            unsorted_list.sort()
            return unsorted_list[length - 1]


    def delete_object(self, object_to_delete):
        """
        Depending on the object type, delete object from
        the dict where its type is
        """
        # store the type of object in a variable
        # check that variable against all the possible
        # Object types and locate the dict
        # then call del(approriate_dict[object_to_delete.key])
        object_type = type(object_to_delete)
        object_dict = {}
        object_keys_list = []
        object_key_map = {}
        object_mapper = ''
        cascaded_objects = []
        if object_type == orderCategory:
            object_dict = self.order_categories
            object_keys_list = self.order_category_keys
            object_key_map = self.order_category_name_key_map
            object_mapper = object_to_delete.name
            cascaded_objects = object_to_delete.get_all_orders(self)

        elif object_type == order:
            object_dict = self.orders
            object_keys_list = self.order_keys
            object_key_map = self.order_name_key_map
            object_mapper = object_to_delete.name
            cascaded_objects = object_to_delete.get_all_steps(self)

        elif object_type == orderStep:
            object_dict = self.order_steps
            object_keys_list = self.order_step_keys   

        else:
            raise TypeError('%s type does not exist in database' % str(object_type)) 

        try:
            del(object_dict[object_to_delete.key])
            object_keys_list.remove(object_to_delete.key)
            if object_mapper:
                del(object_key_map[object_mapper])
            # delete child componet objects
            for cascaded_object in cascaded_objects:
                self.delete_object(cascaded_object)
        except KeyError:
            raise KeyError('%s does not exist' % str(object_type))        

    
    def create_user(self, user_data):
        """Creates a new user and adds the user to self.users"""
        try:
            if self.user_email_key_map[user_data['email']]:
                raise ValueError('User already exists')
        except KeyError:
            # if the key does not exist, pass
            pass
        user_key = self.get_next_key(User)
        try:
            user = User(**user_data, key=user_key)
            user.save(self)
        except:
            raise ValueError('invalid user data')
        return user

    def get_user(self, user_key):
        """
        returns the User object corresponding to user_key or
        None if user does not exist
        """
        if check_type(user_key, int):
            try:
                user = self.users[user_key]
            except KeyError:
                return None
            return user

    def get_user_by_email(self, email):
        """
        Returns a user object corresponding to the email
        passed in or None is user does not exist
        """
        if check_type(email, str):
            try:
                user_key = self.user_email_key_map[email]
            except KeyError:
                return None
            return self.get_user(user_key)
        
    def get_order_category(self, order_category_key):
        """
        Returns the orderCategory object if it exists
        or None if it doesn't
        """
        if check_type(order_category_key, int):
            try:
                order_category = self.order_categories[order_category_key]
            except KeyError:
                return None
            return order_category

    def get_order(self, order_key):
        """
        Returns the order object if it exists
        or None if it doesn't
        """
        if check_type(order_key, int):
            try:
                order = self.orders[order_key]
            except KeyError:
                return None
            return order

    def get_order_step(self, order_step_key):
        """
        Returns the orderStep object if it exists
        or None if it doesn't
        """
        if check_type(order_step_key, int):
            try:
                order_step = self.order_steps[order_step_key]
            except KeyError:
                return None
            return order_step


class User:
    """
    Any user who interfaces with the app falls in this category
    """
    def __init__(self, key, first_name, last_name, email, password):
        if check_type(key, int):
            self.key = key
        if check_type(first_name, str):
            self.first_name = first_name
        if check_type(last_name, str):
            self.last_name = last_name
        if check_type(email, str):
            if check_email_format(email):
                self.email = email
        if check_type(password, str):
            self.password = password
        # a list of order_category keys
        self._order_categories = []

    @property
    def order_categories(self):
        self._order_categories = list(set(self._order_categories))
        return self._order_categories

    def add_order_category(self, key):
        """Adds a new order category key to self._order_categories"""
        self._order_categories.append(key)

    def save(self, database):
        """Saves user to the database appropriately"""
        # add self's key to db's set of user keys
        # Add self to db.users dict with key as self.key
        if check_type(database, Database):
            database.user_keys.append(self.key)
            database.users[self.key] = self
            database.user_email_key_map[self.email] = self.key

    def create_order_category(self, database, order_category_data):
        """
        Creates a new order category and
        adds it to database.order_categories
        """
        if check_type(database, Database):
            # get the last order category key and add 1 
            key = database.get_next_key(orderCategory)
            try:
                # save user in database
                self.save(database)
                category = orderCategory(**order_category_data, key=key, user=self.key)
                category.save(database)
            except TypeError:
                return None
            return category

    def get_all_order_categories(self, database):
        """Returns all the user's order categories"""
        if check_type(database, Database):
            local_order_categories = []
            for category in self.order_categories:
                try:
                    order_category_object = database.order_categories[category]
                except KeyError:
                    self.order_categories.remove(category)
                else:
                    local_order_categories.append(order_category_object)

            return local_order_categories


class orderCategory:
    """
    All categories of orders belong to this class.
    Each orderCategory is created and can be deleted by
    one user
    """
    def __init__(self, key, name, user, description=''):
        if check_type(key, int):
            self.key = key
        if check_type(name, str):
            if len(name.strip()) == 0:
                raise ValueError('name should be a non-empty string')
            self.name = name
        if check_type(description, str):
            self.description = description
        # the creator's key. It does not change
        if check_type(user, int):
            self.user = user
        # the list of child order keys
        self._orders = []

    @property
    def orders(self):
        self._orders = list(set(self._orders))
        return self._orders

    def delete(self, database):
        """Deletes this category of orders and all orders in it"""
        if check_type(database, Database):
            try:
                database.delete_object(self)
                user = database.get_user(self.user)
                if user:
                    user.order_categories.remove(self.key)
            except KeyError:
                raise KeyError('The order category is non-existent in database')

    def create_order(self, database, order_data):
        """
        Creates a new order and
        adds it to database.orders
        """
        if check_type(database, Database):
            # get the last order key and add 1 
            key = database.get_next_key(order)
            try:
                # save category in database
                self.save(database)
                order = order(**order_data, key=key, category=self.key)
                order.save(database)
            except TypeError:
                return None
            return order

    def get_all_orders(self, database):
        """Returns all orders under this category"""
        if check_type(database, Database):
            local_orders = []
            for order in self.orders:
                try:
                    order_object = database.orders[order]
                except KeyError:
                    self.orders.remove(order)
                else:
                    local_orders.append(order_object)

            return local_orders

    def set_description(self, description, database):
        """Edit the description of this order category"""
        if check_type(description, str) and check_type(database, Database):
            self.description = description
            self.save(database)

    def set_name(self, name, database):
        """Edit the name of this order category"""
        if check_type(name, str) and check_type(database, Database):
            if len(name.strip()) == 0:
                raise ValueError('name should be a non-empty string')
            self.name = name
            self.save(database)

    def save(self, database):
        """Saves order category in db and in user"""
        # add self's key to set of order categories of user
        if check_type(database, Database):
            try:
                user = database.users[self.user]
                user.order_categories.append(self.key)
            except KeyError:
                raise KeyError('User should be saved in db first')
            # add self's key to set of db's order_category_keys
            database.order_category_keys.append(self.key)
            # Add self to db.order_categories dict with key as self.key
            database.order_categories[self.key] = self
            # Add self's name and key in db's order_category_name_key_map
            database.order_category_name_key_map[self.name] = self.key


class order:
    """
    Each order are owned by a user and has a category
    """
    def __init__(self, key, name, description, category):
        if check_type(key, int):
            self.key = key
        if check_type(name, str):
            if len(name.strip()) == 0:
                raise ValueError('name should be a non-empty string')
            self.name = name
        if check_type(description, str):
            self.description = description
        # the category key.
        if check_type(category, int):
            self.category = category
        self._order_steps = []
        
    @property
    def order_steps(self):
        self._order_steps = list(set(self._order_steps))
        return self._order_steps

    def change_category(self, new_category, database):
        """Changes the category of the order"""
        # add self's key to new_category's order list
        # remove self's key from old category's order list
        pass

    def delete(self, database):
        """Deleted the order and all its steps"""
        if check_type(database, Database):
            try:
                database.delete_object(self)
                category = database.get_order_category(self.category)
                if category:
                    category.orders.remove(self.key)
            except KeyError:
                raise KeyError('The order is non-existent in database')

    def create_step(self, database, order_step_data):
        """
        Creates a new order step and
        adds it to database.order_steps
        """
        if check_type(database, Database):
            # get the last order_step key and add 1 
            key = database.get_next_key(orderStep)
            try:
                # save order in database
                self.save(database)
                order_step = orderStep(**order_step_data, key=key, order=self.key)
                order_step.save(database)
            except TypeError:
                return None
            return order_step

    def get_all_steps(self, database):
        """returns a list of all steps that belong to self"""
        if check_type(database, Database):
            local_order_steps = []
            for order_step in self.order_steps:
                try:
                    order_step_object = database.order_steps[order_step]
                except KeyError:
                    self.order_steps.remove(order_step)
                else:
                    local_order_steps.append(order_step_object)

            return local_order_steps

    def set_name(self, name, database):
        """Edit the name of this order"""
        if check_type(name, str) and check_type(database, Database):
            if len(name.strip()) == 0:
                raise ValueError('name should be a non-empty string')
            self.name = name
            self.save(database)

    def set_description(self, description, database):
        """Edit the description of this order"""
        if check_type(description, str) and check_type(database, Database):
            self.description = description
            self.save(database)

    def save(self, database):
        """
        Saves the order to the db and to the category's set of orders
        """
        if check_type(database, Database):
            try:
                category = database.order_categories[self.category]
                category.orders.append(self.key)
            except KeyError:
                raise KeyError('Category should be saved in db first')
            # add self's key to set of db's order_keys
            database.order_keys.append(self.key)
            # Add self to db.orders dict with key as self.key
            database.orders[self.key] = self
            # Add self's name and key in db's order_name_key_map
            database.order_name_key_map[self.name] = self.key


class orderStep:
    """Every order contains individual steps"""
    def __init__(self, key,  text_content, order):
        if check_type(key, int):
            self.key = key
        if check_type(text_content, str):
            if len(text_content.strip()) == 0:
                raise ValueError('text content should be a non-empty string')
            self.text_content = text_content
        # the order key. It does not change
        if check_type(order, int):
            self.order = order
        self.key = key
        self.order = order
        self.text_content = text_content

    def delete(self, database):
        """Deleted the order step"""
        if check_type(database, Database):
            try:
                database.delete_object(self)
                order = database.get_order(self.order)
                if order:
                    order.order_steps.remove(self.key)
            except KeyError:
                raise KeyError('The order step is non-existent in database')

    def set_text_content(self, text_content, database):
        """Edit the text_content of this order step"""
        if check_type(text_content, str) and check_type(database, Database):
            if len(text_content.strip()) == 0:
                raise ValueError('text_content should be a non-empty string')
            self.text_content = text_content
            self.save(database)

    def save(self, database):
        """
        Save this object's key in parent order's set of order steps
        and in db
        """
        if check_type(database, Database):
            try:
                order = database.orders[self.order]
                order.order_steps.append(self.key)
            except KeyError:
                raise KeyError('order should be saved in db first')
            # add self's key to set of db's order_step_keys
            database.order_step_keys.append(self.key)
            # Add self to db.order_steps dict with key as self.key
            database.order_steps[self.key] = self


# A global db
db = Database()

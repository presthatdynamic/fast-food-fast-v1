## Project Title
Fast-Food-Fast

## About
Fast-Food-Fast is a food delivery service app for a restaurant

## Getting Started
1. Clone the repository to your computer

	```
	git clone https://github.com/presthatdynamic/fast-food-fast-v1.git
	```

2. In your terminal, enter the directory Fast-Food-Fast

    ```
    cd Fast-Food-Fast
    ```
3. Create and activate your virtualenv. For ubuntu users, see below.

    ```
    virtualenv -p /usr/bin/python3 env

    source env/bin/activate
    ```
4. Install the packages in requirements.txt

    ``` pip install -r requirements.txt ```

5. To start the app, run the following commands in succession still in the same directory

    ```export FLASK_APP=flask_app/run.py```

    ```export APP_SETTINGS="development"```

    ```export SECRET="the-development-key-secret-hide-very-far"```

    ```flask run ```

    _On windows, use 'set' instead of 'export'_
	
## Prerequisites	
1. Bootstrap v4.0.0-alpha
2. Jquery v3.2.1
3. popper.js v1.11.1+
4. Flask v0.12+
5. Python v3.5+

_Other Prerequisites can be found in requirements.txt in this repo_


## Running the tests
1. Clone the repository to your computer (as shown above)
2. Ensure you have the Prerequisites on your system (install the packages in requirements.txt)
3. In your terminal, enter the directory Fast-Food-Fast

``` 
    sh -c 'cd ./flask_app/ && coverage run -m --source=app unittest discover test && coverage report'
    ```
4. Observe the output in your terminal

## Important Links
- [Pivotal Tracker board] https://www.pivotaltracker.com/n/projects/2199787
- [Github] https://github.com/presthatdynamic/fast-food-fast-v1
- [Heroku] https://fastfoodfast-v1.herokuapp.com/






    

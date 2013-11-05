# TacoFancy API

Making an API for https://github.com/sinker/tacofancy

### What I’ve got so far

Got together the relational tables and have the sqlite DB in shape. 

### What’s next

Actually put some routes in the app that generate JSON and make this sucker 
queryable. 

### Want to help?

This whole this is a relatively rudimentary Flask setup. After you ``pip install``
the requirements, you should be able to run the ``prime_db.py`` and get a DB
together. The Flask app is looking for an environmental variable ``TACO_CONN`` to
tell it how to connect to the database. I developed this with sqlite but it should
work with anything that SQLAlchemy supports.

### TODO: Write more docs.

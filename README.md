# TacoFancy API

Making an API for https://github.com/sinker/tacofancy

### Get a random taco

Go here: http://taco-randomizer.herokuapp.com/random/ to get a random Base Layer,
Mixin, Condiment, Seasoning and (whenever someone adds some) Shell. To just get a 
random full taco recipe, call it thusly:

http://taco-randomizer.herokuapp.com/random/?full-taco=true

### What’s next

Get a client presentation together. 

### Want to help?

This whole this is a relatively rudimentary Flask setup. After you ``pip install``
the requirements, you should be able to run the ``prime_db.py`` and get a DB
together. The Flask app is looking for an environmental variable ``TACO_CONN`` to
tell it how to connect to the database. I developed this with sqlite but it should
work with anything that SQLAlchemy supports.

### TODO: Write more docs.

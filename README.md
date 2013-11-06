# TacoFancy API

Making an API for https://github.com/sinker/tacofancy

### Get a random taco

Go here: http://taco-randomizer.herokuapp.com/random/ to get a random Base Layer,
Mixin, Condiment, Seasoning and (whenever someone adds some) Shell. To just get a 
random full taco recipe, call it thusly:

http://taco-randomizer.herokuapp.com/random/?full-taco=true

If you’re a human and not a machine, you can get a random recipe by visiting:

http://taco-randomizer.herokuapp.com/

### Use this data

If you’d like to take advantage of the API that was put together for this, I added
a CORS header to the ``/random/`` path so that you can load it from a javascript app.
I'm hoping to add more features in the coming weeks so, stay tuned.

### Want to help?

This whole this is a relatively rudimentary Flask setup. After you ``pip install``
the requirements, you should be able to run the ``prime_db.py`` and get a DB
together. The Flask app is looking for an environmental variable ``TACO_CONN`` to
tell it how to connect to the database. I developed this with sqlite but it should
work with anything that SQLAlchemy supports.

### TODO: Write more docs.

# TacoFancy API

Making an API for https://github.com/sinker/tacofancy

### Main endpoint

The main endpoint for the API exists at: 

http://taco-randomizer.herokuapp.com/

Visiting that page will also get you a random taco.

### Use this data

If you’d like to take advantage of the API that was put together for this, I added
a CORS header to these paths so that you can load them from a javascript app 
anywhere on the internet.

##### Random Taco

Visiting:

``/random/``

will get you a random Base Layer, Mixin, Condiment, Seasoning and  Shell. To
just get a random full taco recipe, call it thusly:

``/random/?full-taco=true``

##### Contributors

If you’d like to get info about the contributors for a certain recipe,
you can call this endpoint:

``/contributors/:recipe_type/:recipe_slug/``

So to get the contributors for the Delengua (Beef Tounge) Base Layer, do this:

``/contributors/base_layers/delengua_beef_tongue``

Valid layer types are: ``base_layers``, ``mixins``, ``seasonings``, ``condiments``
and ``shells``. To get a mapping of slugs for a given recipe type call this:

``/contributors/:recipe_type/``

##### Contributions

If you’d like to see who has made what contributions to which recipes, call this:

``/contributions/:github_username/``

So, to get all of [Dan Sinker’s](http://github.com/sinker) contributions, call this:

``/contributions/sinker/``

To get a listing of all contributors and their usernames, call:

``/contributions/``

### Want to help?

This whole this is a relatively rudimentary Flask setup. After you ``pip install``
the requirements, you should be able to visit ``/cook/`` to get a DB
together. The Flask app is looking for an environmental variable ``TACO_CONN`` to
tell it how to connect to the database. Depending on what backend you’re using, you
might need to actually create the database, etc before it’ll work.
I developed this with sqlite but you should be able to use any backend that
SQLAlchemy supports.

# TacoFancy API

API for https://github.com/dansinker/tacofancy

## API Endpoints

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

## Development Setup

### Docker (Recommended)

1. Clone the repository
2. Copy `.env.example` to `.env` and add your GitHub token
3. Run: `make up`
4. Initialize database: `make init-db`
5. Load data: `make load-data`
6. API available at `http://localhost:5000/`

### Available Commands

- `make help` - Show all available commands
- `make up` - Start the application
- `make down` - Stop the application
- `make test` - Run tests
- `make init-db` - Initialize database
- `make load-data` - Load data from GitHub
- `make dev` - Run locally (starts database automatically)

### Environment Variables

- `DATABASE_URL` - Database connection string
- `GITHUB_TOKEN` - GitHub API token for higher rate limits (optional)

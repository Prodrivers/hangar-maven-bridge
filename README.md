# hangar-maven-bridge

A bridge application that exposes PaperMC's Hangar as a Maven repository, so that plugins can be managed as dependencies using standard Java tools.

## Features

* Exposes Hangar resources as Maven resources, using the "io.papermc.hangar.<platform>" group ID.
* Supports Paper, Velocity and Waterfall resources
* Supports release channels: append ".<channel>" to the group ID.

Note: this bridge does not have support for authentication. If you want to limit usage of your instance, please protect it with a reverse proxy.

## Usage

Use the Docker image with port 80, or install dependencies using `pip install .` and run `with python app/main.py`.

The Maven repository is accessible at sub-path `/repository/`.

You can also access the API documentation at `/docs`.

## Configuration

Configuration is done using variable environment or a `.env` file. All variables are prefixed with `BRIDGE_`.

* `BRIDGE_HANGAR__API_BASE_URL`: Hangar's API base URL. Only supports API `v1`. Defaults to `https://hangar.papermc.io/api/v1`.
* `BRIDGE_HANGAR__CACHE_PROJECT_EXPIRATION`: How many seconds Hangar projects will be kept in cache
* `BRIDGE_HANGAR__CACHE_VERSION_EXPIRATION`: How many seconds Hangar resource versions will be kept in cache
* `BRIDGE_HANGAR__VERSIONS_LIMIT_PER_BATCH`: The number of versions to fetch in a single batch from the Hangar API
* `BRIDGE_HANGAR__VERSIONS_TOTAL_TO_FETCH`: The total number of versions to fetch from the Hangar API
* `BRIDGE_CACHE__BACKEND`: Cache backend to use, either `inmemory` or `redis`
* `BRIDGE_CACHE__REDIS_URL`: Redis URl to use when cache backend is redis.
* `BRIDGE_CACHE__PREFIX`: Prefix of bridge's data in cache backend
* `BRIDGE_CACHE__POM_EXPIRATION`: How many seconds computed POM for a resource should be kept in cache
* `BRIDGE_CACHE__METADATA_EXPIRATION`: How many seconds computed metadata (essentially version list) for a resource should be kept in cache

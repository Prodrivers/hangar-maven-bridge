# minecraft-maven-bridge

A bridge application that exposes PaperMC's Hangar as a Maven repository, so that plugins can be managed as dependencies using standard Java tools.

## Features

* Exposes Hangar resources as Maven resources, using the "io.papermc.hangar.<platform>" group ID.
  * Supports the following platforms: paper, velocity and waterfall.
  * Supports release channels: append ".<channel>" to the group ID.

* Exposes Modrinth resources as Maven resources, using the "com.modrinth.<loader>" group ID.
  * Supports the following loaders: paper, velocity, waterfall, bungeecord, minecraft, fabric, forge, sponge and folia.
  * Alpha versions reported according to Maven conventions as -SNAPSHOT.

Note: this bridge does not have support for authentication. If you want to limit usage of your instance, please protect it with a reverse proxy.

## Usage

Use the Docker image with port 80, or install dependencies using `pip install .` and run with Python `app/main.py`.

The Maven repository is accessible at sub-path `/repository/`.

You can also access the API documentation at `/docs`.

## Configuration

Configuration is done using variable environment or a `.env` file. All variables are prefixed with `MC_MAVEN_BRIDGE__`.

* `MC_MAVEN_BRIDGE__DEBUG`: Enable debug information in output. Should NEVER be true in production!
* `MC_MAVEN_BRIDGE__HANGAR__API_BASE_URL`: Hangar's API base URL. Only supports API `v1`. Defaults to `https://hangar.papermc.io/api/v1`.
* `MC_MAVEN_BRIDGE__HANGAR__CACHE_PROJECT_EXPIRATION`: How many seconds Hangar projects will be kept in cache
* `MC_MAVEN_BRIDGE__HANGAR__CACHE_VERSION_EXPIRATION`: How many seconds Hangar resource versions will be kept in cache
* `MC_MAVEN_BRIDGE__HANGAR__VERSIONS_LIMIT_PER_BATCH`: The number of versions to fetch in a single batch from the Hangar API
* `MC_MAVEN_BRIDGE__HANGAR__VERSIONS_TOTAL_TO_FETCH`: The total number of versions to fetch from the Hangar API
* `MC_MAVEN_BRIDGE__MODRINTH__API_BASE_URL`: Modrinth's API base URL. Only supports API `v2`. Defaults to `https://api.modrinth.com/v2`.
* `MC_MAVEN_BRIDGE__CACHE__BACKEND`: Cache backend to use, either `inmemory` or `redis`
* `MC_MAVEN_BRIDGE__CACHE__REDIS_URL`: Redis URl to use when cache backend is redis.
* `MC_MAVEN_BRIDGE__CACHE__PREFIX`: Prefix of bridge's data in cache backend
* `MC_MAVEN_BRIDGE__CACHE__POM_EXPIRATION`: How many seconds computed POM for a resource should be kept in cache
* `MC_MAVEN_BRIDGE__CACHE__METADATA_EXPIRATION`: How many seconds computed metadata (essentially version list) for a resource should be kept in cache

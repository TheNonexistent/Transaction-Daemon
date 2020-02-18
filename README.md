# Transaction-Daemon

This file is intended to be ran as a systemd service, the template file for systemd is available in the repo.

This script will start watching for inputs on a redis list and parses the valid transactions that come to the redis list from any source and make the required changes to the main mysql database.

The redis interface was written using Py-Redis.

Note that this script is a part of a larger system which is still under development and may never be released, use with precaution.

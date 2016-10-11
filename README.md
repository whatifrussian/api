## Abstract

The simple flask application implements an API for the <chtoes.li> website.

## Setup

The private configuration and keys supposed to be into `shadow/` directory sibling to `app/` one. This directory is NOT synced with the server by `fab publish` and generally differs between local (debug) and server (production) setup. It should be created manually.

`shadow/config.json` -- overwrites `app/config.json` and has the same format. This file necessary to set credentials for interacting with GitHub Integrations API and keeping its out of version control. Any other settings (like target repository for issues) can be set there to leave repository clean during developing / debugging.

**Warning:** The shadow config non-deeply merged into the public one. While it’s possible to omit a first-level key in the shadow config, the overwritten value should consist all corresponding keys and not only modified ones.

## Deploy

As simple as:

```
user@host api $ fab publish
```

It just sync actual content of the `app/` directory with the server and reloads uwsgi.

## Debug

The website expects `/api/issue/` to be on the same domain as the website. It makes debugging on a local machine tricky, but still possible.

The idea is to run flask's webserver on the same port as a webserver serving the website. Example:

```
user@host website $ fab reserve:debug # or reserve:local
... open http://localhost:8000 in a browser ...
user@host website $ ^C # stop the website's server
... cd to api ...
user@host api $ export FLASK_APP=app/app_main.py
user@host api $ flask run -p 8000
... use the issue form in the browser ...
```

## License

Public domain. You free to use it as you need without any restrictions. No guarantees provided.

Consider LICENSE file for more information.

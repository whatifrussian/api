## Abstract

The simple flask application implements an API for the <chtoes.li> website.

## Deploy

TBD

## Tricks

The website expects `/api/issue/` to be on the same domain as the website. It makes debugging on a local machine tricky, but still possible.

The idea is to run flask's webserver on the same port as a webserver serving the website. Example:

```
user@host website $ fab reserve:debug # or reserve:local
... open http://localhost:8000 in a browser ...
user@host website $ ^C # stop the website's server
... cd to api ...
user@host api $ export FLASK_APP=app_main.py
user@host api $ flask run -p 8000
... use the issue form in the browser ...
```

## License

Public domain. You free to use it as you need without any restrictions. No guarantees provided.

Consider LICENSE file for more information.

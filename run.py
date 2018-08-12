#!/usr/bin/env python3
from app import app

# app.run(debug=app.config['DEBUG'], port=4990,  threaded=True
#         , ssl_context=('/Users/choeminjun/src/noteit/cert/server.crt', '/Users/choeminjun/src/noteit/cert/server.key'))

app.run(debug=app.config['DEBUG'], port=4990,  threaded=True)

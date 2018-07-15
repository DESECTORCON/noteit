#!/usr/bin/env python3
from app import app
app.run(debug=app.config['DEBUG'], port=4990,  threaded=True)

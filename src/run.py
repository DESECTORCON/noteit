from src.app import app
import os

os.chdir('/')
app.run(debug=app.config['DEBUG'], port=4990)

from src.app import app

import os
print(os.getcwd())
app.run(debug=app.config['DEBUG'], port=4990)

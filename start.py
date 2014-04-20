import os
import monkeyapp
app = monkeyapp.create_app(os.environ.get("HEROKU_POSTGRESQL_YELLOW_URL"))
app.config['TESTING'] = True
app.debug = True

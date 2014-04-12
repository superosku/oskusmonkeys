import os
import monkeyapp
app = monkeyapp.create_app(os.environ['DATABASE_URL'])
app.debug=True

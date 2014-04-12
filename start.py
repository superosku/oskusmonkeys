import os
import monkeyapp
app = monkeyapp.create_app(os.environ.get("DATABASE_URL","postgresql://pguser:password/dbname")

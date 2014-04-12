from monkeyapp import create_app
app = create_app('sqlite:////tmp/test.db')
app.run(debug=True)


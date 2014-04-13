from monkeyapp import create_app
#app = create_app('sqlite:////tmp/test.db')
app = create_app('postgresql://monkey:monkey@localhost/monkey')
app.run(debug=True)


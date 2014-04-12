from flask import Flask, request, render_template, g, flash, redirect, url_for, session, Blueprint
from monkeyapp import models, forms#, app
from monkeyapp.database import db_session

api = Blueprint('api' , __name__)

@api.route("/")
def index():
	return render_template('index.html')

@api.route("/monkeys", methods=["post", "get"])
def monkeys():
	form = forms.MonkeyForm(request.form)
	if request.method == 'POST' and form.validate():
		user = models.User(form.name.data, form.email.data, form.age.data)
		db_session.add(user)
		db_session.commit()
		flash("New monkey added")
		return redirect(url_for(".monkeys"))
	monkeys = models.query_users(order=request.args.get('ord'))
	return render_template('monkeys.html', monkeys=monkeys.all(), form=form, order=request.args.get('ord'))

@api.route("/monkey/<int:ident>", methods=["post", "get"])
def view_monkey(ident):
    try: monkey = models.User.query.filter_by(id=ident).one()
    except: return redirect(404)

    form = forms.FriendForm(request.form)
    form.user.query_factory = monkey.get_non_friends

    best_friend_form = forms.BestFriendForm(user=monkey.best_friend)
    best_friend_form.user.query_factory = monkey.friends.all
    if request.method == 'POST':
        if form.validate():
            monkey.add_friend(form.user.data)
            flash("Friend added")
            form = forms.FriendForm(request.form)
            form.user.query_factory = monkey.get_non_friends
        else:
            flash("Form not valid")
    return render_template('monkey.html', monkey=monkey, form=form, best_friend_form=best_friend_form)

@api.route("/monkey/<int:ident>/add_best_friend/", methods=["post", "get"])
def add_best_friend(ident, methods=["post"]):
	try:
		monkey = models.User.query.filter_by(id=ident).one()
	except:
		return redirect(404)
	form = forms.BestFriendForm(request.form)
	form.user.query_factory = monkey.friends.all
	if form.validate():
		friend = form.user.data
		monkey.make_best_friend(friend)
		flash("Best friend updated")
	else:
		flash("Form not valid")
                return redirect(404)
	return redirect(url_for(".view_monkey", ident=ident))

@api.route("/remove_friend/<int:ident1>/<int:ident2>", methods=["post", "get"])
def remove_friend(ident1, ident2):
    try:
        monkey = models.User.query.filter_by(id=ident1).one()
        friend = models.User.query.filter_by(id=ident2).one()
    except:
        return redirect(404)
    form = forms.RemoveForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            monkey.remove_friend(friend)
            flash("Friendship removed")
        except:
            flash("Couldnt remove friendship")
        return redirect(url_for(".view_monkey", ident=ident1))
    return render_template('remove_friend.html', monkey1=monkey, monkey2=friend, form=form)

@api.route("/edit/<int:ident>", methods=["post", "get"])
def edit_monkey(ident):
	try:
		monkey = models.User.query.filter_by(id=ident).one()
	except:
		return redirect(404)
	form = forms.MonkeyForm(request.form, obj=monkey)
	if request.method == 'POST' and form.validate():
		form.populate_obj(monkey)
		db_session.commit()
		flash("Monkey updated")
		return redirect(url_for(".view_monkey", ident=ident))
	return render_template('edit_monkey.html', monkey=monkey, form=form)

@api.route("/remove/<int:ident>", methods=["get", "post"])
def remove_monkey(ident):
    try:
        monkey = models.User.query.filter_by(id=ident).one()
    except:
        return redirect(404)
    form = forms.RemoveForm(request.form)
    if request.method == 'POST' and form.validate():
        db_session.delete(monkey)
        db_session.commit()
        flash("Monkey removed")
        return redirect(url_for(".monkeys"))
    return render_template('remove_monkey.html', monkey=monkey, form=form)

@api.app_errorhandler(404)
def handle_404(error):
    return render_template('page_not_found.html'), 404



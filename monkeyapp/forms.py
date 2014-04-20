from wtforms import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import model_form_factory

from models import User
from monkeyapp import database


def query_users():
    return User.query


class FriendForm(Form):
    user = QuerySelectField(
        get_label=u"name")


class BestFriendForm(Form):
    user = QuerySelectField(
        get_label=u"name",
        allow_blank=True,
        blank_text=u"None")


class RemoveForm(Form):
    pass


ModelForm = model_form_factory(Form)


class MonkeyForm(ModelForm):
    class Meta:
        model = User

    def get_session(self):
        return database.db_session

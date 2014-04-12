import sys
import os
import unittest
import tempfile

import monkeyapp
from monkeyapp.database import db_session, init_db, create_all, drop_all
from monkeyapp.models import User

class MyBaseCase(unittest.TestCase):
    def setUp(self):
        self.app = monkeyapp.create_app('sqlite+pysqlite:////tmp/test23.db')
        self.app.debug = True
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        create_all()
    def tearDown(self):
        db_session.remove()
        drop_all()
        self.ctx.pop()

class TestDatabase(MyBaseCase):
    def test_database_empty(self):
        u = monkeyapp.models.User.query.all()
        self.assertEqual(len(u), 0, "Database should be empty this point, it is " + str(len(u)))
    def test_add_monkeys(self):
        db_session.add(User("Test1", "test@test.fi", 20))
        db_session.add(User("Test2", "test1@test.fi", 20))
        db_session.commit()
        u = monkeyapp.models.User.query.all()
        self.assertEqual(len(u), 2, "Database should be empty this point")
    def test_friendship(self):
        db_session.add(User("Test1", "test1@test.fi", 20))
        db_session.add(User("Test2", "test2@test.fi", 20))
        db_session.commit()
        users = User.query.all()
        users[0].add_friend(users[1])
        self.assertEqual(users[0].friends.count(), 1, "This user should have 1 friend")
        self.assertEqual(users[1].friends.count(), 1, "Also the friend should have 1 friend")
        users[0].remove_friend(users[1])
        self.assertEqual(users[0].friends.count(), 0, "Removing friends should also work")
        self.assertEqual(users[1].friends.count(), 0, "Removing friends should also work")
    def test_best_friend(self):
        db_session.add(User("Test1", "test1@test.fi", 20))
        db_session.add(User("Test2", "test2@test.fi", 20))
        db_session.commit()
        users = User.query.all()
        users[0].add_friend(users[1])
        users[0].make_best_friend(users[1])
        self.assertEqual(users[0].best_friend, users[1], "Should be his best friend")
        self.assertEqual(users[1].best_friend, None, "Should not have best friend")
        users[0].remove_friend(users[1])
        self.assertEqual(users[0].best_friend, None, "Removing friendship should also remove best friendship")
        users = User.query.all()
    def test_best_friend_circular_conflict(self):
        db_session.add(User("Test1", "test1@test.fi", 20))
        db_session.add(User("Test2", "test2@test.fi", 20))
        db_session.commit()
        users = User.query.all()
        users[0].add_friend(users[1])
        users[0].make_best_friend(users[1])
        users[1].make_best_friend(users[0])
        users[0].make_best_friend(None)
        assert users[0].best_friend == None

class TestRequests(MyBaseCase):
    def test_no_monkeys(self):
        rw = self.client.get('/monkeys')
        assert "No monkeys" in rw.data
    def test_add_monkey(self):
        rw = self.client.post('/monkeys', data=dict(
            name="newmonkeyname",
            email="t@t.t",
            age=20,
        ), follow_redirects=True)
        assert "newmonkeyname" in rw.data
    def test_add_monkey_wrongly(self):
        rw = self.client.post('/monkeys', data=dict(
            name="",
            email="t@t.t",
            age=20,
        ), follow_redirects=True)
        assert not "New monkey added" in rw.data
        assert "Field required" in rw.data
    def test_same_names(self):
        rw = self.client.post('/monkeys', data=dict(
            name="newmonkeyname",
            email="t@t.fi",
            age=20,
        ), follow_redirects=True)
        rw = self.client.post('/monkeys', data=dict(
            name="newmonkeyname",
            email="t@t.fi",
            age=20,
        ), follow_redirects=True)
        assert "Already exists" in rw.data
    def test_404(self):
        rw = self.client.get('/monkey/100', follow_redirects=True)
        assert "Not Found" in rw.data

class TestRequestsOccupied(MyBaseCase):
    def setUp(self):
        super(TestRequestsOccupied, self).setUp()
        for i in range(20):
            db_session.add(User("Test%i"%i, "test%i@test.fi"%i, 20))
        db_session.commit()
    def test_user_count(self):
        assert User.query.count() == 20
    def test_view(self):
        user = User.query.filter_by(name="Test9").one()
        rw = self.client.get('/monkey/%i'%user.id)
        assert "test9@test.fi" in rw.data
        assert "None" in rw.data #Best friend should be none
    def test_best_friend(self):
        user = User.query.filter_by(name="Test9").one()
        user2 = User.query.filter_by(name="Test10").one()
        rw = self.client.post('/monkey/%i/add_best_friend/'%user.id, data=dict(
            user=user2.id), follow_redirects=True)
        assert "Form not valid" in rw.data
        user.add_friend(user2)
        rw = self.client.post('/monkey/%i/add_best_friend/'%user.id, data=dict(
            user=user2.id), follow_redirects=True)
        #sys.stderr.write(rw.data)
        assert "Best friend updated" in rw.data
    def test_add_friend(self):
        user = User.query.filter_by(name="Test9").one()
        user2 = User.query.filter_by(name="Test7").one()
        rw = self.client.post('/monkey/%i'%user.id, data=dict(
            user=user2.id), follow_redirects=True)
        assert "Friend added" in rw.data
    def test_remove_friend(self):
        users = User.query.all()
        users[0].add_friend(users[1])
        users[0].add_friend(users[2])
        users[0].add_friend(users[3])
        rw = self.client.get('/remove_friend/%i/%i'%(users[0].id,users[1].id))
        assert "Sure to remove friendship" in rw.data
        assert users[0].name in rw.data
        assert users[1].name in rw.data
        rw = self.client.post('/remove_friend/%i/%i'%(users[0].id,users[1].id), follow_redirects=True)
        assert "Friendship removed" in rw.data
        rw = self.client.post('/remove_friend/%i/%i'%(users[0].id,users[4].id), follow_redirects=True) #Not friends
        assert "Couldnt remove friendship" in rw.data
    def test_remove_monkey(self):
        user = User.query.first()
        rw = self.client.get('/remove/%i'%user.id)
        assert "Sure to remove" in rw.data
        rw = self.client.post('/remove/%i'%user.id, follow_redirects=True)
        assert "Monkey removed" in rw.data
    def test_existing_details(self):
        rw = self.client.post('/monkeys', data=dict(
            name="Jou", email="test1@test.fi", age=10))
        assert "Already exists" in rw.data
        rw = self.client.post('/monkeys', data=dict(
            name="Test1", email="t@t.fiiii", age=10))
        assert "Already exists" in rw.data
    def test_invalid_email(self):
        rw = self.client.post('/monkeys', data=dict(
            name="Jou", email="not an email", age=10))
        assert "Invalid email" in rw.data
    def test_invalid_age(self):
        rw = self.client.post('/monkeys', data=dict(
            name="Jou", email="jou@test.fi", age="moi"))
        assert "Not a valid integer value" in rw.data
    def test_edit(self):
        user = User.query.first()
        rw = self.client.get('/edit/%i'%user.id)
        assert user.name in rw.data
        rw = self.client.post('/edit/%i'%user.id, follow_redirects=True, data=dict(
            name="Joumies",
            email=user.email,
            age=user.age))
        assert "Joumies" in rw.data
        rw = self.client.post('/edit/%i'%user.id, follow_redirects=True, data=dict(
            name="Test5",
            email=user.email,
            age=user.age))
        assert "Already exists" in rw.data
        rw = self.client.post('/edit/%i'%user.id, follow_redirects=True, data=dict(
            name=user.name,
            email="not an email",
            age=user.age))
        assert "Invalid email" in rw.data


if __name__ == '__main__':
    unittest.main()


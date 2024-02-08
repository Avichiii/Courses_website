from course.models import Users, Items
from course import db


# using this classs admin related functionality is implemented
class AdminPanel(object):
    # def __init__(self, user_obj, item_obj):
    #     self.user_obj = user_obj
    #     self.item_obj = item_obj

    @property
    def getusers(self):
        users = Users.query.all()
        return users
    
    @property
    def getitems(self):
        items = Items.query.all()
        return items

    
    def deleteuser(self, username):
        user = Users.query.filter_by(username=username).first()   
        db.session.delete(user)
        db.session.commit()
        

    def deleteitem(self, itemname):
        item = Items.query.filter_by(name=itemname).first()   
        db.session.delete(item)
        db.session.commit()

    def settokens(self, username, token_amount):
        token_already_has = Users.query.filter_by(username=username).first().tokens_owned
        updated_token = int(token_already_has) + int(token_amount)
        Users.query.filter_by(username=username).update({'tokens_owned': updated_token})
        db.session.commit()

    def display_user_courses(self, user_obj):
        users = Users.query.all()
        for user in users:
            if user == user_obj:
                return user.items_owned



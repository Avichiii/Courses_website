from course import db, bcrypt
from course import login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# this is a associative table // creates many-many relations
course_owner = db.Table('course_owner',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('items_id', db.Integer(), db.ForeignKey('items.id'))
)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=50), nullable=False)
    tokens_owned = db.Column(db.Integer(), nullable=False, default=500)
    # adding secondary table for many-many relationship
    items_owned = db.relationship('Items', secondary=course_owner, backref='owned_users', lazy=True)

    @property
    def styled_token(self):
        # returns a formated version of tokens_owned (uses one liner)
        return f"{str(self.tokens_owned)[0:-3]}, {str(self.tokens_owned)[-3:]}t" if len(str(self.tokens_owned)) >= 4 else f"{str(self.tokens_owned)}t"

    # setting up getter
    @property
    def password(self):
        # it will return the hashed password to the caller
        return self.password_hash
    
    # setting up setter
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')


    def password_checking(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_object):
        # if item object is already in users items_owned object, user should not able to purchase the item.
        return self.tokens_owned >= item_object.token and self.username != item_object.uploader and (item_object not in self.items_owned)
    
    def __str__(self) -> str:
        return f"User: {self.username}"


class Items(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    uploader = db.Column(db.String(length=30), nullable=False)
    url = db.Column(db.String(length=240), nullable=False, unique=True)
    # from coin -> token
    token = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)  

    def will_be_owned(self, user_obj):
        # adding the course to the users // items_owned can be used as a list
        user_obj.items_owned.append(self)
        # substracting the token value
        user_obj.tokens_owned -= self.token
        
        # fetching course uploder object
        course_uploader_obj = Users.query.filter_by(username=self.uploader).first()
        # adding the token value to the uploaders token_worth
        '''
        we are transferring the token to the uploaders object
        '''
        course_uploader_obj.tokens_owned += self.token
        db.session.commit()

    def __repr__(self) -> str:
        return f"Items: {self.name}"
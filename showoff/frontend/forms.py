# Imports {{{
from wtforms import TextField, PasswordField, validators
from flask.ext.wtf import Form
# }}}

class LoginForm(Form):
    username = TextField('Username', validators=[validators.Required(message='Username is required.')])
    password = PasswordField('Password', validators=[validators.Required(message='Password is required.')])

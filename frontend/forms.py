# Imports {{{
from flaskext.wtf import Form, TextField, PasswordField, Required
# }}}

class LoginForm(Form):
    username = TextField('Username', validators=[Required(message='Username is required.')])
    password = PasswordField('Password', validators=[Required(message='Password is required.')])

#!/usr/bin/python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField, DateField, DateTimeField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange



from app.v1.forms.storeforms import *
from app.v1.forms.productforms import *
from app.v1.forms.priceforms import *
from app.v1.forms.searchforms import *
#!/usr/bin/python3
"""
Base for Store Forms
"""
from app.v1.forms import DataRequired, FlaskForm, Length, StringField, SubmitField

class BaseStoreForm(FlaskForm):
    """
    Base Store Form
    """
    store_name = StringField("Name of Store", validators=[DataRequired("A store cannot be nameless"), Length(max=255)])
    submit = SubmitField(label="Create New Store")

    def validate(self, extra_validators=None):
        # check if all required fields are filled
        rv = super(BaseStoreForm, self).validate(extra_validators)
        if not rv:
            return False
        return True
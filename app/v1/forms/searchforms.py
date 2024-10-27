#!/usr/bin/python3
"""
Base for Search Product Forms
"""
from app.v1.forms import DataRequired, FlaskForm, IntegerField, Length, StringField, SubmitField, SelectField

class BaseSearchProductForm(FlaskForm):
    """
    Base Search Product Form
    """
    search_string = StringField("Name of Product", validators=[DataRequired("Provide a search string"), Length(max=255)])
    product_stores  = SelectField('List of Stores')
    submit = SubmitField(label="Create New Product")

    def validate(self, extra_validators=None):
        # check if all required fields are filled
        rv = super(BaseSearchProductForm, self).validate(extra_validators)
        if not rv:
            return False
        return True
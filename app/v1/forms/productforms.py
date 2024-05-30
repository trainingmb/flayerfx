#!/usr/bin/python3
"""
Base for Product Forms
"""
from app.v1.forms import DataRequired, FlaskForm, IntegerField, Length, StringField, SubmitField, SelectField

class BaseProductForm(FlaskForm):
    """
    Base Product Form
    """
    product_name = StringField("Name of Product", validators=[DataRequired("A product cannot be nameless"), Length(max=255)])
    product_link = StringField("Link to the Product", validators=[DataRequired("A product cannot be without a Link"), Length(max=255)])
    product_reference = IntegerField("Reference for the Product", validators=[DataRequired("A product cannot be without a reference")])
    product_stores  = SelectField('List of Stores')
    submit = SubmitField(label="Create New Product")

    def validate(self, extra_validators=None):
        # check if all required fields are filled
        rv = super(BaseProductForm, self).validate(extra_validators)
        if not rv:
            return False
        return True
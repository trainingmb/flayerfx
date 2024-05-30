#!/usr/bin/python3
"""
Base for Price Forms
"""
from app.v1.forms import BooleanField, DecimalField, DateTimeField, DataRequired, FlaskForm, Length, SelectField, StringField, SubmitField

class BasePriceForm(FlaskForm):
    """
    Base Price Form
    """
    price_products = SelectField('Products')
    price_amount = DecimalField("Amount", validators=[DataRequired("A Price must an Amount")])
    price_is_discount = BooleanField('Is Discount', default=False)
    price_fetched_at = DateTimeField("Created At", validators=[DataRequired("This is Required")])
    submit = SubmitField(label="Create New Price")

    def validate(self, extra_validators=None):
        # check if all required fields are filled
        rv = super(BasePriceForm, self).validate(extra_validators)
        if not rv:
            return False
        return True
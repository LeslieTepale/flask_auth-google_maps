from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import *

class csv_upload(FlaskForm):
    file = FileField()
    submit = SubmitField()

class location_register_form(FlaskForm):
    title = TextAreaField('Title', [validators.DataRequired(),], description="Enter a location name")

    longitude = TextAreaField('Longitude', [validators.DataRequired(),], description="Enter a location longitude")
    latitude = TextAreaField('Latitude', [ validators.DataRequired(),], description="Enter a location latitude")
    population = TextAreaField('Population', [validators.DataRequired(),], description="Enter a location population")
    submit = SubmitField()

class location_edit_form(FlaskForm):
    title = TextAreaField('Title', [validators.length(min=6, max=300)],
                          description="Please add location title")
    longitude = TextAreaField('Longitude', [validators.length(min=6, max=300)],
                          description="Please add location longitude")
    latitude = TextAreaField('Latitude', [validators.length(min=6, max=300)],
                          description="Please add location latitude")
    population = TextAreaField('Population', [validators.length(min=6, max=300)],
                          description="Please add location population")
    submit = SubmitField()
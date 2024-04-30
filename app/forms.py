
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired


class EditProfileForm(FlaskForm):
  title = StringField('Title')
  first_name = StringField('First Name')
  last_name = StringField('Last Name')
  position = StringField('Position')
  phone_number = StringField('Phone Number')
#   email = StringField('Email')
  email = StringField('Email', render_kw={'readonly': True})
  address = StringField('Address')
  date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')

  # Initialize tutor-specific fields as None or as actual fields based on is_tutor
  teaching_subjects = StringField('Teaching Subjects')
  years_of_experience = StringField('Years of Experience')
  qualification = StringField('Qualification')
  introduction = TextAreaField('Introduction')

  def __init__(self, is_tutor=False, *args, **kwargs):
    super(EditProfileForm, self).__init__(*args, **kwargs)
    self.is_tutor = is_tutor

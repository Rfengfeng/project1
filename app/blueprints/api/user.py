from flask import Blueprint, request, session
from app.models.user import Role, User
from app.models import Image
from app.database import db
from app.utils.hash import generate_password_hash, is_strong_password
from app.utils.session import get_current_user, require_login, require_roles, set_current_user
from app.utils.string_helper import generate_salt
from flask_hashing import Hashing
from uuid import uuid4
import os

user_api = Blueprint('user_api', __name__)
hashing = Hashing()


@user_api.route('logout')
def logout():
  '''
  Log the user out
  '''
  # Remove user from session
  session.pop('user', None)
  return {'success': True}


@user_api.route('password/<int:id>', methods=['PUT', 'POST'])
@require_login()
def update_password(id: int):
  '''
  Update the password of a user by ID
  '''
  current_user = get_current_user()
  user = db.session.query(User).filter_by(id=id).first()

  if not user:
    return {'success': False, 'error': 'User not found'}

  # Only allow managers to update other users' passwords
  if user.id != current_user.id and current_user.id != Role.manager.value:
    return {'success': False, 'error': 'Unauthorized'}

  old_password = request.form.get('old_password')
  new_password = request.form.get('password')

  # Check if the old password is correct
  if generate_password_hash(old_password, user.salt) != user.password:
    return {'success': False, 'error': 'Your old password is incorrect'}

  # Check if the new password is strong
  if not is_strong_password(new_password):
    return {'success': False, 'error': 'Please use a stronger password with at least 8 characters and a mix of character types'}

  # Update the password
  user.salt = generate_salt()
  user.password = generate_password_hash(new_password, user.salt)

  db.session.merge(user)
  db.session.commit()
  session.pop('user', None)
  return {'success': True, 'message': 'Password updated'}


@user_api.route('profile_picture', methods=['POST'])
@require_login()
def update_profile_picture():
  '''
  Update the profile picture of the current user
  '''
  user = db.session.query(User).get(get_current_user().id)

  # Check if the image is present
  image_file = request.files.get('image')
  if not image_file:
    return {'success': False, 'error': 'Please select an image file'}

  # Check mime
  if not image_file.mimetype.startswith('image'):
    return {'success': False, 'error': 'Only images are allowed'}

  # Use uuid as filename
  filename = f'{uuid4()}.' + image_file.filename.split('.')[-1]
  # Move image to uploads folder
  image_path = f'uploads/{filename}'
  save_path = os.path.join('app', 'static', 'uploads', filename)
  image_file.save(save_path)

  old_image = None

  # Check if user has an existing profile picture
  if user.profile_image_id:
    old_image = db.session.query(Image).get(user.profile_image_id)

  # Create new image
  new_image = Image(title=user.full_name, path=image_path,
                    size=os.path.getsize(save_path))

  # Replace old image with new image
  db.session.add(new_image)
  db.session.flush()
  user.profile_image_id = new_image.id
  db.session.merge(user)

  # Delete old image
  if old_image:
    old_image.delete(db.session)

  db.session.commit()
  set_current_user(user)
  return {'success': True, 'message': 'Profile picture updated', 'user': user.to_dict()}


@user_api.route('profile_picture', methods=['DELETE'])
@require_login()
def delete_profile_picture():
  '''
  Delete the profile picture of the current user
  '''
  user = db.session.query(User).get(get_current_user().id)
  profile_image = user.profile_image

  if profile_image:
    # Remove the profile image from the user
    user.profile_image_id = None
    db.session.merge(user)

    # Delete the image from the database
    profile_image.delete(db.session)
    db.session.commit()
  return {'success': True, 'message': 'Profile picture deleted'}

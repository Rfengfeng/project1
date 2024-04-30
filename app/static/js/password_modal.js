/**
 * Event listener for the password form submission
 * @param {Event} event 
 */
function changePassword(event) {

  event.preventDefault()
  const form = event.target;
  const url = form.action;
  const formData = new FormData(form);

  // Check if the form is valid
  if (!form.checkValidity()) {
    return;
  }

  // Check if the passwords match
  if (formData.get('password') !== formData.get('confirm_password')) {
    $('#error-message').text('Passwords do not match').removeClass('d-none')
    return;
  }

  $('#error-message').text('').addClass('d-none')

  // Send a PUT request to the API to change the password
  fetch(url, {
    method: 'PUT',
    body: formData,
  }).then(resp => {
    if (resp.ok) {
      return resp.json()
    } else {
      throw new Error('Password change failed')
    }
  }).then(data => {
    if (data.success) {
      // Reset the form and show a success message
      form.reset();
      // Redirect to the login page and show a success message
      flashAndReload('Password changed successfully', 'success', '/user/login')
      $('#password-modal').modal('hide')
    } else {
      $('#error-message').text(data.error).removeClass('d-none')
    }
  }).catch(e => {
    // Show an error message
    fireToastMessage('Password change failed', 'danger')
  })
}

function toggleVisibility(inputId) {
  const input = document.getElementById(inputId);
  if (input.getAttribute('type') === 'password') {
    input.setAttribute('type', 'text');
  } else {
    input.setAttribute('type', 'password');
  }
  $(input).parent().find('.password-toggle i').toggleClass('fa-eye fa-eye-slash');
}

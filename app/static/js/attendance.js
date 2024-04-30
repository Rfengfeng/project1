var url, form, modal, selectedBookings, formData

/**
 * Handles the click event on the attend button
 * @param {Event} e 
 */
function onAttendClick(e) {
  button = e.target;
  url = button.getAttribute('data-url');
  selectedBookings = null;
  modal = $('#confirmation-modal');
  modal.modal('show');
}

/**
 * Handles the click event on the attend button 
 * @param {Event} e 
 */
function onAttendFormSubmit(e) {
  e.preventDefault();
  const form = e.target;
  url = form.getAttribute('action');

  // Get the selected bookings from the form
  formData = new FormData(form)
  modal = $('#confirmation-modal');
  modal.modal('show');
}

function submitAttendance(e) {
  // Submit the attendance by sending a POST request to API
  fetch(url, {
    method: 'POST',
    body: formData ?? undefined,
  }).then(resp => {
    if (resp.ok) {
      return resp.json()
    }
  }).then(data => {
    if (data.success) {
      // Close the modal and reload the page
      modal.modal('hide')
      flashAndReload('Attendance recorded', 'success')
    } else {
      modal.modal('hide')
      // Show an error message
      fireToastMessage(data.error || data.message || 'An error occurred', 'danger')
    }
  })
}

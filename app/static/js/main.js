function onPageLoad() {
  // On page load, show the toast if there is a flash message
  const searchParams = new URLSearchParams(window.location.search)

  if (searchParams.has('_fm') || searchParams.has('_fc')) {
    // Remove the flash message from the URL
    searchParams.delete('_fm');
    searchParams.delete('_fc');
    const searchString = searchParams.toString();
    window.history.replaceState(null, null, window.location.pathname + (searchString ? `?${searchString}` : ''));
  }

  // Fire all toasts
  $('.toast').toast('show');

  // Register tooltips
  $('[data-bs-toggle="tooltip"]').tooltip();

  // Check form validation
  $(".needs-validation").on('submit', function (e) {
    console.log(this)
    if (!this.checkValidity()) {
      e.preventDefault();
      e.stopPropagation();
      $(this).addClass('was-validated');
    }
  });

  pollReminders(); // Start polling for reminders
}

// Register the onPageLoad function to be called when the page is loaded
$(onPageLoad)

function fireToastMessage(message, category = 'primary') {
  // Create dynamic a toast message and show it
  const toastContainer = $(`
  <div aria-live="polite" aria-atomic="true" class="position-fixed toast-fixed">
    <div class="toast-container top-50 start-50 translate-middle">
      <div class="toast align-items-center text-bg-${category} border-0"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
          data-bs-delay="3000">
        <div class="d-flex">
          <div class="toast-body"></div>
          <button type="button"
                  class="btn-close btn-close-white me-2 m-auto"
                  data-bs-dismiss="toast"
                  aria-label="Close"></button>
        </div>
      </div>
    </div>
  </div>
  `).appendTo(document.body);

  // Trigger the toast message
  const toast = toastContainer.find('.toast');
  toast.find('.toast-body').text(message);
  toast.on('hidden.bs.toast', () => {
    // Remove the toast from the DOM when it is hidden
    toast.remove()
  });
  toast.toast('show');
}

/**
 * Show a toast with the given message and category
 * and redirect to the given URL
 * @param {string} message message to show
 * @param {string} category colour of the message
 * @param {string?} url URL to redirect to and show the message
 */
function flashAndReload(message, category, url=null) {
  const searchParams = new URLSearchParams(window.location.search)
  searchParams.set('_fm', message);
  searchParams.set('_fc', category);
  const searchString = searchParams.toString();

  // Combine the URL with the search string and redirect
  window.location = (url || window.location.pathname) +(searchString ? `?${searchString}` : '');
}

var reminderTimer;

/**
 * Poll the server for unread reminders
 */
function pollReminders() {
  let timerDelay = 10000;

  // Define the runner function
  const runner = () => {
    if (!window.current_user) {
      return
    }

    // Fetch the number of unread reminders
    fetch('/api/reminder/unread/count')
      .then(response => response.json())
      .then(data => {
        const reminders = data.reminders;
        // Update the number of reminders in the navbar
        if (reminders) {
          $('#nav-num-reminders').text(reminders)
          $('#nav-item-reminders').removeClass('d-none')
        } else {
          $('#nav-item-reminders').addClass('d-none')
        }
      })
      .then(() => {
        // Set the next timer
        reminderTimer = setTimeout(runner, timerDelay)
        timerDelay = Math.min(Math.round(timerDelay * 1.15), 60000)
      })
  };

  // Clear the previous timer
  if (reminderTimer) {
    clearTimeout(reminderTimer)
  }
  runner()
}

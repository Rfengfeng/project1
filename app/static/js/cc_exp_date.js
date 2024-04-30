function onPageLoad() {
    // Validate credit card expiration date format and future date
    $("#cc-expiration").on("input", function() {
      var input = $(this).val();
      if (input.length === 2 && input.indexOf("/") === -1) {
        $(this).val(input + "/");
      }
    }).on("blur", function() {
      var ccExpirationInput = $(this);
      var input = ccExpirationInput.val();
      var parts = input.split("/");
      var isValid = parts.length === 2 && parts[0].length === 2 && parts[1].length === 2;
  
      if (isValid) {
        var month = parseInt(parts[0], 10);
        var year = parseInt(parts[1], 10) + 2000; // Convert YY to YYYY
        var expDate = new Date(year, month, 0); // The day is set to 0 to get the last day of the previous month
        var currentDate = new Date();
  
        if (expDate < currentDate || month < 1 || month > 12) {
          isValid = false;
        }
      }
  
      if (!isValid) {
        ccExpirationInput[0].setCustomValidity("Invalid or past expiration date.");
        ccExpirationInput.siblings(".invalid-feedback").show();
      } else {
        ccExpirationInput[0].setCustomValidity("");
        ccExpirationInput.siblings(".invalid-feedback").hide();
      }
    });
  
    $(".needs-validation").on("submit", function(e) {
      if (!this.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass("was-validated");
      }
    });
  }
  
 
  
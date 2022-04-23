//help for validation from https://www.w3schools.com/js/js_validation.asp
function validate_account_form(form) {
    if (form.username.value.length == 0){
      alert("käyttäjänimi on pakollinen")
      return false;
    }
    if (form.password.value.length == 0){
      alert("salasana on pakollinen")
      return false;
    }
    return true;

  }
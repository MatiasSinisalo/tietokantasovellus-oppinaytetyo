//help for validation from https://www.w3schools.com/js/js_validation.asp
function validate_book_addition_form(form) {
    if (form.name.value.length == 0){
      alert("kirjan nimi on pakollinen")
      return false;
    }
    if (form.publishDate.value.length == 0){
      alert("julkaisupäivä on pakollinen")
      return false;
    }

    if (form.authors.value.length == 0){
      alert("Kirjailijat on pakollinen")
      return false;
    }

    if (form.amountFree.value.length == 0){
      alert("lainattavissa olevat kirjat on pakollinen")
      return false;
    }

    if (form.amountOverall.value.length == 0){
      alert("kaikkien kirjojen maara on pakollinen")
      return false;
    }

    if (len(form.content.filename) < 1){
      alert("tiedosto on pakollinen")
      return false;
    }


    return true;

  }
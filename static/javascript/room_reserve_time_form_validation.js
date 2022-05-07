function validate_book_addition_form(form) {
   
    minutePatter = "/0/"

    if (validateDateValues(form.startMinute, form.startHour, form.startDay, form.startMonth, form.startYear) == false){
         return false
    }

    if (validateDateValues(form.endMinute, form.endHour, form.endDay, form.endMonth, form.endYear) == false){
        return false
   }

    return true;

  }

  function validateDateValues(minute, hour, day, month, year){
    //minute validation
    minuteRegEx = "[]"
    if (minute.value.length < 1){
        alert("aloitus minuutin kuuluu olla muotoa: MM")
        return false;
      }
      if (minute.value.length > 2){
          alert("aloitus minuuttin kuuluu olla muotoa: MM")
          return false;
      }
  
      if (minute.value > 60)
      {
  
          alert("minuutin kuuluu olla < 60")
          return false;
      }
      if (minute.value < 0)
      {
          alert("minuutin kuuluu olla > 0")
          return false;
      }
      
      //Hour validation
      if (hour.value.length < 1){
          alert("aloitus minuutin kuuluu olla muotoa: HH")
          return false;
        }
      
        if (hour.value.length > 2){
            alert("aloitus minuuttin kuuluu olla muotoa: HH")
            return false;
      }
      
      if (hour.value > 24)
      {
  
          alert("tunnin kuuluu olla <= 24")
          return false;
      }
      if (hour.value < 0)
      {
          alert("tunnin kuuluu olla > 0")
          return false;
      }
  
      //day validation
      if (day.value.length < 1){
          alert("paivan kuuluu olla muotoa: DD")
          return false;
        }
      
        if (day.value.length > 2){
            alert("paivan kuuluu olla muotoa: DD")
            return false;
      }
      
      if (day.value > 31)
      {
  
          alert("paivan kuuluu olla <= 31")
          return false;
      }
      if (day.value < 0)
      {
          alert("paivan kuuluu olla > 0")
          return false;
      }
      //Month validation
      if (month.value.length < 1){
          alert("kuukauden kuuluu olla muotoa: MM")
          return false;
        }
      
        if (month.value.length > 2){
            alert("kuukauden kuuluu olla muotoa: MM")
            return false;
      }
      
      if (month.value > 12)
      {
  
          alert("kuukauden kuuluu olla <= 12")
          return false;
      }
      if (month.value < 0)
      {
          alert("kuukauden kuuluu olla > 0")
          return false;
      }
     
      //Year validation
      if (year.value.length < 4){
        alert("vuoden kuuluu olla muotoa: YYYY")
        return false;
      }
      
      if (year.value.length > 4){
          alert("vuoden kuuluu olla muotoa: YYYY")
          return false;
      }
      
      if (year.value < 0)
      {
          alert("vuoden kuuluu olla > 0")
          return false;
      }
      
      return true

  }


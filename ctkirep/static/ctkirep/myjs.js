function filterTables(id) {
    var x = $("#" + id).val();
    if (x == "stable0") {
      $("table[id*='stable']").show();
    }
    else {
      $("#" + x).show();
      $("table[id!='" + x +"']").hide();
    }
  }
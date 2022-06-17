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

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});
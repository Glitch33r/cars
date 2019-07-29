$('#filter_brand').change(function () {
  let mark_id = $(this).val()
  let url_path = '/api/models/' + mark_id
  $.get(url_path, function (data) {
    $('.model-down').addClass('fas fa-caret-down').html('<select class="form-control" name="model" id="filter_model" required></select>')
    $('#filter_model').html('<option selected value="">Выбери модель</option>')
    data.models.forEach(function (element) {
      $('#filter_model').append('<option value="' + element.id + '">' + element.name + '</option>')
    })
  })
});
$('.Search').on('click', function (e) {
  var modelValue = $('#filter_model option:selected').val();
  var modelName = $('#filter_model option:selected').text();
  var markName = $('#filter_brand option:selected').text();
  if (modelValue) {
    e.preventDefault();
    $.ajax({
      url: '/analitic/mileage/',
      type: 'post',
      data: { 'model': modelValue },
      success: function (response) {
        $('.graph').css('display', 'block');
        var years = response['years']
        var fuels = response['fuels']
        var dataSets = []
        for (fuel in fuels) {
          var mydict = {
            'label': fuel,
            'data': fuels[fuel],
            //'backgroundColor': $.Color([ 255, 0, 100 ]),
            //'hoverBackgroundColor': this.convertHex(rgb(100,200,255), 70),
          }
          dataSets.push(mydict)
        }
        var chartData = {
          labels: years,
          datasets: dataSets
        };
        var chLine = $('#chLine');
        if (chLine) {
          new Chart(chLine, {
            type: 'line',
            data: chartData,
            options: {
              title: {
                display: true,
                text: 'Статистика пробега по годам ' + markName + ' ' + modelName,
                position: 'top'
              },
              scales: {
                yAxes: [{
                  ticks: {
                    beginAtZero: true
                  }
                }]
              },
              legend: {
                display: true
              }
            }
          });
        }
      }
    })
  };
});
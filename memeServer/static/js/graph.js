function graph(meme, base_url) {
  $.getJSON("/api/history?meme=" + meme, function (data) {
    var formattedData = new Array();
    
    // format data to [time, price] format
    for (var trade in data) {
      formattedData.push([data[trade].time * 1000, data[trade].price]);
    }
    
    Highcharts.chart('chartContainer', {
        chart: {
            panning: true,
            // hold shift to pan
            panKey: 'shift',
            zoomType: 'x'
        },
        title: {
            text: ""
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            floor: 0,
            title: {
                text: 'Stock value'
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            area: {
                // higher the cropThreshold, the more points you can graph
                // while retaining zoom functionality
                cropThreshold: 1000,
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },

        series: [{
            type: 'area',
            name: 'Stock value',
            data: formattedData
        }]
    });
  });
}

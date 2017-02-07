function graph(meme, base_url) {
  $.getJSON(base_url + "/api/history", {meme:meme}, function(input) {
    
    var dataPoints= input.map(function(pt) { 
      return {
        x:new Date(Math.round(pt["time"]*1000)), 
        y:pt["price"]
      };
    });
    
    // Create a data point at now.
    dataPoints.unshift({
      x:new Date(Date.now()), 
      y:dataPoints[0]["y"]
    });

    // pick a reasonable interval
    var start_hour = new Date(Math.round(input[0]['time']));
    start_hour = start_hour.getHours();
    var end_hour = new Date(Date.now());
    end_hour = end_hour.getHours();
    var interval = Math.round(end_hour - start_hour / 5);
    interval = interval < 2 ? 2 : interval;
    
    var chart = new CanvasJS.Chart("chartContainer",
      {
        axisX:{
          title: "time",
          gridThickness: 2,
          interval:interval, 
          intervalType: "hour",        
          valueFormatString: "MMM DD hh TT", 
          labelAngle: -20
        },
        axisY:{
          title: "price"
        },
        data: [
          {        
            type: "line",
            dataPoints: dataPoints
          }
        ]
      });
    chart.render();
  });
}

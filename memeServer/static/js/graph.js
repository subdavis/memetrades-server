function graph(meme, base_url) {
  $.getJSON(base_url + "/api/history", {meme:meme}, function(input) {

    if (input.length == 0){
      console.log("Nothing to graph...");
      return;
    }
    
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

    var chart = new CanvasJS.Chart(
      "chartContainer",
      {
        axisX:{
          title: "time",
          gridThickness: 2,
          // interval:interval, 
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
            lineThickness: 3,
            dataPoints: dataPoints
          }
        ]
      });
    chart.render();
  });
}

function graph(meme, base_url) {
  $.getJSON(base_url + "/api/history", {meme:meme}, function(input) {
    var dataPoints= input.map(function(pt) { return {x:new Date(pt["time"]), y:pt["price"]}});
    dataPoints.push({x:new Date(Date.now()), y:dataPoints[dataPoints.length - 1]["y"]});
    var chart = new CanvasJS.Chart("chartContainer",
    {
      // title:{
      //   text: "Price of " + meme },

      axisX:{
        title: "time",
        gridThickness: 2,
        interval:2, 
        intervalType: "hour",        
        valueFormatString: "hh TT K", 
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

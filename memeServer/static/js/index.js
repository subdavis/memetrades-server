var sortby = function(a, b) {return b[3] - a[3]};
var base_url = ""
var graphed = "";

function tableCreate(el, data)
{
    var tbl  = document.createElement("table");
    for (var i = 0; i < data.length; ++i)
    {
        var tr = tbl.insertRow();
        tr.setAttribute("class", "economy");

        var td_price = tr.insertCell();
        td_price.appendChild(document.createTextNode('$' + data[i]['price']));
        var td_trend = tr.insertCell();
        td_trend.appendChild(document.createTextNode(data[i]['trend'] ? trend_symbol(data[i]['trend']): ""));
        var td_value = tr.insertCell();
        td_value.appendChild(document.createTextNode(data[i]['name']));
    }
    el.append(tbl);

}

var oldData;
var oldDeltas = {};
function updateMarket(){
    $.getJSON(base_url+'/api/stocks', function(data) {
        if (graphed == ""){
            graphed = data[0]['name'];
            graph(graphed, base_url);
        }
        var market = $("#jsonM");
        market.empty();
        tableCreate(market, data);
        $('td').click(function() {
            document.getElementById("meme").value = this.innerText;
            graph(this.innerText, base_url);
        });
        oldData = data;
     });
}

function update() {
  $.getJSON(base_url+'/api/me', function(data) {
        var portfolioText = "Money: " + data['money'] + "\n";
        portfolioText += "Stocks: \n";
        for (var i=0;i<data['stocks'].length;i++){
            portfolioText+= "  " + data['stocks'][i]['price'] + " : " + data['stocks'][i]['name'] + "\n";
        }
        document.getElementById("jsonP").innerHTML = portfolioText;
        updateMarket();
    });
}

function sell() {
    var meme = document.getElementById("meme").value;
    $.get(base_url+"/api/sell", {meme: meme}, update)
}


function buy() {
    var meme = document.getElementById("meme").value;
    $.get(base_url+"/api/buy", {meme: meme}, update)
}

function init(){
    api_key = getUrlParameter("api_key");
    update();
    // while (hottest == ""){}
    setInterval(updateMarket, 3000);
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function trend_symbol(num) {
    if (num > 0)
        return '⬆';
    return '⬇';
}

// Entry point

window.onload = init;

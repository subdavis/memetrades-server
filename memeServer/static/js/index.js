var base_url = ""
var graphed;

function is_authenticated(){
    var portfolio = $("#jsonP");
    if (portfolio.length > 0)
        return true;
    return false;
}

function board_display(meme){
    $("#selected-stock").text(meme);
    $.get('/api/stock', {meme:meme}, function(data){
        $("#selected-price").text("Price: $" + data['price']);
        $("#selected-trend").empty().text("Trend: ").append(trend_symbol(data['trend']));
        $("#selected-link").attr("href", "http://memetrades.com?active=" + meme);
    });
    graphed = meme;
    graph(meme, base_url);
    $(".canvasjs-chart-canvas").css("position", "relative");
}

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
        td_trend.appendChild(data[i]['trend'] ? trend_symbol(data[i]['trend']) : "");
        var td_value = tr.insertCell();
        td_value.appendChild(document.createTextNode(data[i]['name']));
    }
    el.append(tbl);
}

function updateMarket(){
    $.getJSON(base_url+'/api/stocks', function(data) {
        if (graphed === undefined)
            board_display(data[0]['name']);
        var market = $("#jsonM");
        market.empty();
        tableCreate(market, data);
        $('td').click(function() {
            if (is_authenticated())
                document.getElementById("meme").value = this.innerText;
            board_display(this.innerText);
        });
        oldData = data;
     });
}

function update() {
    if (is_authenticated()){
        $.getJSON(base_url+'/api/me', function(data) {
            var portfolioText = "Money: " + data['money'] + "\n";
            portfolioText += "Stocks: \n";
            var total_value = 0;
            for (var i=0;i<data['stocks'].length;i++){
                if (data['stocks'][i]['amount'] > 0){
                    total_value += data['stocks'][i]['value'];
                    portfolioText+= "  " + data['stocks'][i]['amount'] + " : " + data['stocks'][i]['name'] + "\n";
                }
            }
            portfolioText = "Holdings value: " + total_value + "\n" + portfolioText;
            document.getElementById("jsonP").innerHTML = portfolioText;
            updateMarket();
        });
    }
}

function sell() {
    var meme = document.getElementById("meme").value;
    $.get(base_url+"/api/sell", {meme: meme}, update);
}

function buy() {
    var meme = document.getElementById("meme").value;
    $.get(base_url+"/api/buy", {meme: meme}, update);
}

function remove(){
    /* Admin only. Don't bother, the backend will check your permissions */
    var meme = document.getElementById("meme").value;
    $.get(base_url+"/api/admin/stock/delete", {meme: meme}, update);
}

function init(){
    api_key = getUrlParameter("api_key");
    update();
    var active = getUrlParameter("active");
    if (active)
        board_display(active);
    updateMarket();
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
            return sParameterName[1] === undefined ? false : sParameterName[1];
        }
    }
};

function trend_symbol(num) {
    var span = document.createElement('span');
    if (num > 0){
        span.innerHTML = '⬆';
        span.className = 'trend_up'
    }
    else{
        span.innerHTML = '⬇';
        span.className = 'trend_down'
    }
    return span;
}

// Entry point

window.onload = init;

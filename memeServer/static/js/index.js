var base_url = ""
var graphed;
var selected_meme;
var page;
var portfolio_list;
var me;
var last_load;

function is_authenticated(){
    var portfolio = $("#account-info");
    return (portfolio.length > 0);
}

function get_view(){
    var market = $("#market");
    if (market.length > 0)
        return "market"
    var recent = $("#recent");
    if (recent.length > 0)
        return "recent"
    return "portfolio"
}

function get_selected_meme(){}

function board_display(meme){
    console.log('Displaying ' + meme);
    $("#selected-stock").text(meme);
    $("#selected-stock").attr('meme', meme);
    $.get('/api/stock', {meme:meme}, function(data){
        if (data['name']){
            // the meme existed
            $("#selected-price").text("Price: $" + data['price']);
            $("#selected-trend").empty().text("Trend: ").append(trend_symbol(data['trend']));
            $("#selected-link").attr("href", "/stock/" + data['_id']['$oid']);
        } else {
            $("#selected-price").text("Price: $1");
            $("#selected-trend").empty().text("?");
        }
    });
    graphed = meme;
    selected_meme = meme;
    graph(meme, base_url);
}

function tableCreate(el, data, query)
{
    el.empty();
    var tbl  = document.createElement("table");
    
    if (data.length >= 1){
        var trh = tbl.insertRow();
        var th_amount = trh.insertCell();
        th_amount.appendChild(document.createTextNode('#'));
        var th_price = trh.insertCell();
        th_price.appendChild(document.createTextNode('price'));
        var th_trend = trh.insertCell();
        th_trend.appendChild(document.createTextNode('trend'));
        var th_name = trh.insertCell();
        th_name.appendChild(document.createTextNode('name'));
        trh.setAttribute('class', 'economy-header');
    }

    for (var i = 0; i < data.length; ++i)
    {
        var tr = tbl.insertRow();
        tr.setAttribute("class", "economy");
        tr.setAttribute("meme", data[i]['name']);

        var td_amount = tr.insertCell();
        if ('amount' in data[i]){
            if (data[i]['amount'] == 0)
                break;
            td_amount.appendChild(document.createTextNode(data[i]['amount']));
        } else {
            // TODO get_portfolio_amount()
            td_amount.appendChild(document.createTextNode(''));
        }

        var td_price = tr.insertCell();
        td_price.appendChild(document.createTextNode('$' + data[i]['price']));

        var td_trend = tr.insertCell();
        td_trend.appendChild(data[i]['trend'] 
            ? trend_symbol(data[i]['trend']) 
            : document.createTextNode(""));

        var td_value = tr.insertCell();
        td_value.appendChild(document.createTextNode((data[i]['blacklisted'] ? '(BANNED**) ' : '') + data[i]['name']));
        td_value.setAttribute('class', 'meme-name');
    }

    if (query) {
        //prompt to "add new"
        var newtext = "Inspect meme " + query;

        var trh = tbl.insertRow();
        var th_new = trh.insertCell();
        trh.setAttribute('meme', query);
        trh.setAttribute('class', 'economy');
        th_new.appendChild(document.createTextNode(newtext));
        th_new.setAttribute('id', 'create-meme');
        th_new.setAttribute('colspan', 4);
        $("#create-meme").off('click');
    }

    el.append(tbl);

    $('tr.economy').click(function() {
        if (is_authenticated())
            document.getElementById("meme").value = this.getAttribute('meme');
        board_display(this.getAttribute('meme'));
    });
}

function updateAccount(holdings, money){
    // console.log("Update account...");
    $("#account-money").text("$"+money);
    $("#account-holdings").text("$"+holdings);
}

function referral(){
    if (is_authenticated() && me){
        prompt("Share your code with friends: you'll both get an extra 300 memebucks.", "http://memetrades.com" + "/login?r=" + me['referral_code']);
    }
}

function updateMarket(){
    $.getJSON(base_url+'/api/stocks',{page:page}, function(data) {
        if (graphed === undefined)
            board_display(data[0]['name']);
        var market = $("#jsonM");
        market.empty();
        tableCreate(market, data);
    });
}

function updatePortfolio(meme) {
    // Called, among other things, when buy and sell are clicked.
    if (is_authenticated()){
        $.getJSON(base_url+'/api/me', function(data) {
            me = data;
            portfolio_list = data['stocks'];
            updateAccount(data['stock_value'], data['money']);
            //update table on portfolio page.
            if (get_view() == "portfolio")
                tableCreate($("#jsonM"), data['stocks']);           
        });
    }
}

function updateRecent(){
    $.getJSON(base_url+'/api/recent', function(data) {
        tableCreate($("#jsonM"), data);
    });
}

function update(meme){
    // Decide what to do depending on what view we are in....
    if (is_authenticated())
        updatePortfolio();
    var view = get_view()
    if (view == "market")
        updateMarket();
    if (view == "recent")
        updateRecent();
    if (meme)
        board_display(meme);
}

function sell() {
    console.log("Sell");
    var meme = $("#selected-stock").attr('meme');
    $.get(base_url+"/api/sell", {meme: meme}, function(data){
        if (data['status'] == 'fail')
            toastr.error(data['reason']);
        else
            toastr.success('Queued one SELL.');
        update(meme);
    });
}

function buy() {
    console.log("Buy");
    var meme = $("#selected-stock").attr('meme');
    $.getJSON(base_url+"/api/buy", {meme: meme}, function(data){
        if (data['status'] == 'fail')
            toastr.error(data['reason']);
        else
            toastr.success('Queued one BUY.');
        update(meme);
    });
}

function remove(){
    var meme = $("#selected-stock").attr('meme');
    /* Admin only. Don't bother, the backend will check your permissions */
    if (confirm("Admin remove " + meme + "?")){
        $.get(base_url+"/api/admin/stock/delete", {meme: meme}, function(data){
            if (data['status'] == 'fail')
                toastr.error(data['reason']);
            else
                toastr.success('Admin - Removed');
            update(meme);
        });
    }
}

function search(){
    var query = $("#meme").val();
    $.getJSON(base_url+"/api/search", {q:query}, function(data){
        var elem = $("#search-results-table");
        elem.empty();
        tableCreate(elem, data, query);
    })
}

function init(){
    var active = $("#selected-stock").attr('meme');
    if (active != '') // TODO: Slight hack...  Maybe I can do this better.
        board_display(active);
    page = $("#pagenumber").text();
    update();
    setInterval(update, 3000);
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

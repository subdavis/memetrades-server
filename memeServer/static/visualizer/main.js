var svg = d3.select("svg"),
	width = window.innerWidth || +svg.attr("width"),
	height = window.innerHeight || +svg.attr("height");

// Set width and height
svg.attr("width", width).attr("height", height);

// Zoom
svg.call(d3.zoom().on("zoom", function () {
	svg.select("g").attr("transform", d3.event.transform); // Austin wrote this
}));

// TODO more colors
var color = d3.scaleOrdinal(d3.schemeCategory20);

var menu = [
{
	title: "Buy stock",
	action: (elm, d, i) => { buyMeme(d.name); }
},
{ divider: true },
{
	title: "Sell stock",
	action: (elm, d, i) => { sellMeme(d.name); }
},
];


// Force directed graph simulation
var simulation = d3.forceSimulation()
	.force("link", d3.forceLink().id((d) => d.id))
	.force("gravity", d3.forceManyBody().strength(1)) // d.mass?
	.force("collide", d3.forceCollide((d) => d.radius))
	.force("center", d3.forceCenter(width / 2, height / 2));

// Tooltip
var tooltip = d3.select("body")
	.append("div")
	.attr("class", "d3-tip")
	.style("position", "absolute")
	.style("z-index", "10")
	.style("visibility", "hidden");

// onready
$(document).ready(function() {
	// Fetch data from JSON
	getData();
});

function getData() {
	d3.json("/api/stocks", function (error, json) {
		if (error) throw error;

		// Scrape JSON
		var data = scrapeJSON(json);

		/*
		// Create link
		var link = svg.append("g")
		.attr("class", "links")
		.selectAll("line")
		.data(graph.links)
		.enter().append("line")
		.attr("stroke-width", (d) => Math.sqrt(d.value));
		 */

		// Create node
		var node = svg.append("g")
			.attr("class", "nodes")
			.selectAll("circle")
			.data(data)
			.enter().append("circle")
			.attr("class", "node")

		updateNode(node);

		simulation
			.nodes(data)
			.on("tick", ontick);

		/* simulation.force("link")
		   .links(graph.links);
		 */

		function ontick() {
			// Update values
			/*
			   link
			   .attr("x1", (d) => d.source.x)
			   .attr("y1", (d) => d.source.y)
			   .attr("x2", (d) => d.target.x)
			   .attr("y2", (d) => d.target.y);
			 */

			node
				.attr("cx", (d) => d.x)
				.attr("cy", (d) => d.y);
		}
	});
}

function updateData() {
	d3.json("/api/stocks", function (error, json) {
		if (error) throw error;

		// Scrape data
		var data = scrapeJSON(json);

		// Update nodes and add new ones as needed
		var node = svg.select("g")
			.selectAll("circle")
			.data(data)
			.enter().append("circle") // don't use this
			.attr("class", "node");

		updateNode(node);

		node.each((d) => {
			console.log(d.radius);
			d.fx = d.x;
			d.fy = d.y;
		})

		simulation.nodes(data);

	});
}

/* Events */
function ondragstart(d) {
	if (!d3.event.active) simulation.alphaTarget(0.3).restart();
	d.fx = d.x;
	d.fy = d.y;
}

function ondrag(d) {
	d.fx = d3.event.x;
	d.fy = d3.event.y;
	moveTooltip(d);
}

function ondragend(d) {
	if (!d3.event.active) simulation.alphaTarget(0);
	d.fx = null;
	d.fy = null;
}

function onmouseover(d) {
	d3.select(this).transition()
		.attr("style", (d) => "stroke: black; stroke-width: " + (0.045 * d.radius < 3 ? 3 : 0.045 * d.radius));
	showTooltip(d);
}

function onmouseout(d) {
	d3.select(this).transition()
		// .attr("style", (d) => "stroke: " + d.color + "; stroke-width: 0");
		.attr("style", (d) => "stroke: black; stroke-width: 0");
	hideTooltip();
}

function onmousemove(d) {
	moveTooltip(d);
}

function onclick(d) {
	// TODO tmp
	updateData();
}

/* Helpers */
// Scrape JSON into a list of stocks of { name, price }
function scrapeJSON(json) {
	var data = [];
	Object.entries(json).forEach(([key, value]) => {
		var stock = { name: key, price: value };
		data.push(stock);
	});
	return data;
}

function updateNode(node) {
	// Set cutom properties
	// Don't use arrow function => because `this` is rebound
	node.each(function (d, i, nodes) {
		d.color = color(d.name);
		d.color_hover = color(d.name+1); // change it a bit TODO
		d.radius = d.price;
	});

	// Title (on hover)
	node.append("title")
		.text((d) => d.name);

	// Size and color
	node.attr("r", (d) => d.radius)
		.attr("fill", (d) => d.color)
		.attr("style", "stroke-width: 0");

	// Mouse events
	node.call(d3.drag()
			.on("start", ondragstart)
			.on("drag", ondrag)
			.on("end", ondragend))
		.on("mouseover", onmouseover)
		.on("mouseout", onmouseout)
		.on("mousemove", onmousemove)
		.on("click", onclick)
		.on("contextmenu", d3.contextMenu(menu, {
			onOpen: () => { },
			onClose: () => { }
		}));
};

function showTooltip(d) {
	var html = "<strong>Stock:</strong> <span style='color:red'>" + d.name + "</span><br>";
	html += "<strong>Price:</strong> <span style='color:red'>" + d.price + "</span><br>";
	tooltip.style("visibility", "visible").html(html);
}

function moveTooltip(d) {
	// TODO put directly above node
	tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
}

function hideTooltip() {
	tooltip.style("visibility", "hidden");
}

/* Business logic */
var iframe = d3.select("body").append("iframe").node();

// Buy meme
function buyMeme(meme, n) {
	n = n || 1;
	var get_url = "http://hgreer.com/meme/buy?meme="+meme;
	iframe.src = get_url;
	// alert("Bought meme: " + meme);
}

// Sell meme
function sellMeme(meme, n) {
	n = n || 1;
	var get_url = "http://hgreer.com/meme/sell?meme="+meme;
	iframe.src = get_url;
	// alert("Sold meme: " + meme);
}

let timeoutID;
let timeout = 1000;


function setup() {
	document.getElementById("theButton").addEventListener("click", makePost, true);
	timeoutID = window.setTimeout(poller, timeout);
}

function makePost() {
	console.log("Sending POST request");
	const msg = document.getElementById("a").value     //grab input from html

	fetch("/add_message", {
			method: "post",
			headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
			body: `msg=${msg}`
		})
		.then((response) => {
			return response.json();
		})
		.then((result) => {
			//updateList(result);
			clearInput();
		})
		.catch(() => {
			console.log("Error posting new items!");
		});
}

function poller() {
	console.log("Polling for new messages");
	fetch("/check_message")
		.then((response) => {
			return response.json();
		})
		.then(updateList)
		.catch(() => {
			console.log("Error fetching items!");


			
			window.location.href = "{{ url_for('welcome') }}";
		});
}

function updateList(result) {
	console.log("Updating the table");
	//const tab = document.getElementById("theTable");
	//while (tab.rows.length > 0) {
	//	tab.deleteRow(0);
	//}
	
	for (var i = 0; i < result.length; i++) {
		addLi(result[i]);
	}
	timeoutID = window.setTimeout(poller, timeout);
}

function addLi(item) {
	const listRef = document.getElementById("msgList");
	//const newLi = listRef.insertRow();   // create a <tr> tag

	//for (var i = 0; i < row.length; i++) {
	if(item.length>0){
		const newLi = document.createElement("LI"); // create and insert a <td> element
		const newText = document.createTextNode(item);
		newLi.appendChild(newText);
		
		listRef.appendChild(newLi)
	}
		//}

	//var x = document.createElement("LI");
	//var t = document.createTextNode("Coffee");
	//x.appendChild(t);
	//document.getElementById("myList").appendChild(x);


}

function clearInput() {
	console.log("Clearing input");
	document.getElementById("a").value = "";
}

window.addEventListener("load", setup, true);

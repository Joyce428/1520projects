function setup() {
	document.getElementById("createButton").addEventListener("click", createRoomPost, true);
}

function makePost() {
	console.log("Sending POST request");
	const msg = document.getElementById("a").value     //grab input from html
	//const two = document.getElementById("b").value
	//const three = document.getElementById("c").value
	
	fetch("/add_message", {
			method: "post",
			headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
			body: `msg=${msg}`
		})
		.then((response) => {
			return response.json();
		})
		.then((result) => {
			updateList("msgList",result);
			clearInput();
		})
		.catch(() => {
			console.log("Error posting new items!");
		});
}

function createRoomPost(){
	console.log("Sending create room POST request");
	msg='create'

	fetch("/create_room", {
			method: "post",
			headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
			body: `msg=${msg}`
		})
		.then((response) => {
			return response.json();
		})
		.then((result) => {
			updateList("myRList", result);
			clearInput();
		})
		.catch(() => {
			console.log("Error posting new items!");
		});
}



function updateList(listID,result) {
	console.log("Updating the table");
	//const tab = document.getElementById("theTable");
	//while (tab.rows.length > 0) {
	//	tab.deleteRow(0);
	//}
	
	for (var i = 0; i < result.length; i++) {
		addLi(listID,result[i]);
	}
	
}

function addLi(listID, item) {
	const listRef = document.getElementById(listID);
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

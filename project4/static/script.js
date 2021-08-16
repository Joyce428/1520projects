function setup() {
	document.getElementById("theButton").addEventListener("click", makePost, true);
	document.getElementById("purButton").addEventListener("click", makePurchase, true);
}

function makeDelete(itemId){
	let url = "cats/"+itemId;
	console.log("Sending DELETE request");

	fetch(url, {
			method: "delete"
		})
		.then(() => {
			//updateList(result);
			updateCats();
		})
		.catch(() => {
			console.log("Error deleting category!");
		});
}


function makePost() {
	console.log("Sending POST request");
	const one = document.getElementById("a").value
	const two = document.getElementById("b").value
	//const three = document.getElementById("c").value
	my_str = '{"name":"'+one+'","limit":'+two+'}';


	fetch("/cats", {
			method: "post",
			//headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
			headers: { "Content-type": "application/json"},
			//body: `name=${one}&limit=${two}`
			body: my_str
		})
		.then((response) => {
			//console.log(`Got this response: ${response[0]}`);
			//console.log(response);
			return response.json();
		})
		.then((result) => {
			//updateList(result);
			updateCats();
			clearInput();
		})
		.catch(() => {
			console.log("Error posting new items!");
		});
}

function updateUncatPurs(){
	fetch("/uncat")
	.then((response) => {
		return response.json();
	})
	.then((result) => {
		let str = "amount of uncategorized purchases: "+ result[0];
		addPurLi(str);
	})
	.catch((err) => {
		console.log(`Error updating purchases: ${err}`);
	});
}

function updatePurs() {
	fetch("/purchases")
		.then((response) => {
			return response.json();
		})
		.then((response) => {
			console.log("hello");
			console.log(response);
			updatePurList(response);
		})
		.catch((err) => {
			console.log(`Error updating purchases: ${err}`);
		});
}

function updateCats() {
	fetch("/cats")
		.then((response) => {
			return response.json();
		})
		.then((response) => {
			console.log("hello");
			console.log(response);
			// Should repopulate the list
			updateList(response);
		})
		.catch((err) => {
			console.log(`Error updating for new categories: ${err}`);
		});
}

function makePurchase() {
	console.log("Sending POST request");
	console.log("Sending POST request");
	const one = document.getElementById("amount").value
	const two = document.getElementById("date").value
	const three = document.getElementById("category").value
	my_str = '{"amount":'+one+',"date":"'+two+ '","category":"'+three+'"}';

//	"pur1":{"amount": 0, "date": "04-04-2020", "category": "house"}

	fetch("/purchases", {
			method: "post",
			//headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
			headers: { "Content-type": "application/json"},
			//body: `name=${one}&limit=${two}`
			body: my_str
		})
		.then((response) => {
			return response.json();
		})
		.then((result) => {
			//updateTable(result);
			updateCats();
			updatePurs();
			updateUncatPurs();
			clearInput();
		})
		.catch(() => {
			console.log("Error posting new items!");
		});
}

function updateList(result) {
	console.log(" Updating the category table");
	let listRef = document.getElementById("theList");
	while( listRef.firstChild ){
		listRef.removeChild( listRef.firstChild );
	}

	for (var cat in result) {
		let str = "";
		for(var key in result[cat]){
			if(key=="name"){
				str= result[cat][key]+str;
			}

			if(key=="remaining"){
				if(result[cat][key]<0){
					let num = 0-result[cat][key];
					str = str+" | you are $"+num+" over budget ";
				}else{
					str = str+" | budget remaining: $"+result[cat][key]+" ";
				}
			}

			if(key=="limit"){
				str=str+" | initial budget: $"+result[cat][key];
			}
		}
		addLi(str,cat);
	}
	
}


function addLi(item,btnID) {
	let listRef = document.getElementById("theList");
	if(item.length>0){
		let newLi = document.createElement("LI"); // create and insert a <td> element
		let newText = document.createTextNode(item);
		newLi.appendChild(newText);

		let newBtn = document.createElement("button");
		newBtn.setAttribute("id", btnID);
		//newBtn.setAttribute("onclick","makeDelete('{{btnID}}')")
		newBtn.textContent="Delete";
		newBtn.onclick=function(){makeDelete(newBtn.id)};
		newLi.appendChild(newBtn);

		listRef.appendChild(newLi);

	}
}

function updatePurList(result) {
	console.log("Updating the purchase table");
	let listRef = document.getElementById("purList");
	while( listRef.firstChild ){
		listRef.removeChild( listRef.firstChild );
	}


	//Date: 04-04-2020 | Category: house | Amount: 10
	for (var pur in result) {
		let str = "";
		for(var key in result[pur]){
			//a c d
			if(key=="amount"){
				str= " | Amount: "+result[pur][key];
			}

			if(key=="category"){
				str = " | Category: "+result[pur][key]+str;
			}

			if(key=="date"){
				str="Date: "+result[pur][key]+str;
			}
			//console.log(key);
		}
		addPurLi(str);
	}
	
}

function addPurLi(item) {
	let listRef = document.getElementById("purList");
	if(item.length>0){
		let newLi = document.createElement("LI"); // create and insert a <td> element
		let newText = document.createTextNode(item);
		newLi.appendChild(newText);
		listRef.appendChild(newLi)
	}
}

function clearInput() {
	console.log("Clearing input");
	document.getElementById("a").value = "";
	document.getElementById("b").value = "";
	//document.getElementById("c").value = "";
	document.getElementById("amount").value= "";
	document.getElementById("date").value= "";
	document.getElementById("category").value= "";
}

window.addEventListener("load", setup, true);

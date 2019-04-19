$('.ui.accordion').accordion({
	selector: {
		trigger: '.acc-title'
	}
});

$('.ui.dropdown').dropdown();

$(document).ready(function(){$(".rating").rating();});

/*************  Create Element ******************
*	Input: string1, string2, string3, string4, boolean1, string5
* Output: template card with provided parameters in scrollable list
**************************************************/
function createElement(lib,floor,section,distance,isquiet,chance,rank,link){
	var registered = false
	//get reference to the list
	var S_list = document.getElementById("List_accordion")
	//get reference to the template holder
	const template_holder = document.getElementById("card_template")
	//get reference to the template of library card
	let content = template_holder.content;
	console.log(content);
	//clone template for library card
	var card_template = content.cloneNode(true)

	//setAttributes for library card
	if(lib == 'UGL'){
	    console.log('UGL')
	    card_template.getElementById("Library_image1").src = src="/static/img/LibraryImages/UGL/Ugl1.jpeg";
	    card_template.getElementById("Library_image2").src = src="/static/img/LibraryImages/UGL/Ugl2.jpeg";
	    card_template.getElementById("reference_item").id = 'UGL';
	    card_template.getElementById("LibraryNameText").innerText = "Undergraduate Library";
	    registered = true
	}
	else if (lib == 'GG') {
	    console.log('GG')
	    card_template.getElementById("Library_image1").src = src="/static/img/LibraryImages/Grainger/Grainger1.jpeg";
	    card_template.getElementById("Library_image2").src = src="/static/img/LibraryImages/Grainger/Grainger2.jpeg";
	    card_template.getElementById("reference_item").id = 'GG';
	    card_template.getElementById("LibraryNameText").innerText = "Grainger Library";
	    registered = true
	}
	else if (lib == 'MainLib') {
	    console.log('GG')
	    card_template.getElementById("Library_image1").src = src="/static/img/LibraryImages/MainLib/MainLib1.jpeg";
	    card_template.getElementById("Library_image2").src = src="/static/img/LibraryImages/MainLib/MainLib2.jpeg";
	    card_template.getElementById("reference_item").id = 'Main';
	    card_template.getElementById("LibraryNameText").innerText = "Main Library";
	    registered = true
	}else if (lib == "Chem"){
		console.log('Chem')
	    card_template.getElementById("Library_image1").src = src="/static/img/LibraryImages/Chem/Chem1.jpg";
	    card_template.getElementById("Library_image2").src = src="/static/img/LibraryImages/Chem/Chem2.jpg";
	    card_template.getElementById("reference_item").id = 'Chem';
	    card_template.getElementById("LibraryNameText").innerText = "Chemistry Library";
		registered = true
	}else if (lib == "Aces"){
		console.log('Aces')
	    card_template.getElementById("Library_image1").src = src="/static/img/LibraryImages/Aces/Aces1.jpg";
	    card_template.getElementById("Library_image2").src = src="/static/img/LibraryImages/Aces/Aces2.jpg";
	    card_template.getElementById("reference_item").id = 'Aces';
	    card_template.getElementById("LibraryNameText").innerText = "ACES Library";
		registered = true
	}else{
	    console.log('Library not defined')
	}

	if(registered == true)
	{
		//general settings
		card_template.getElementById("Floor").innerText = floor;
		card_template.getElementById("Section").innerText = section;
		card_template.getElementById("Distance").innerText = distance;
		card_template.getElementById("Chance").innerText = chance;
		card_template.getElementById("Reserve_button").href = link;
		card_template.getElementById("Rank").innerText = rank;

		console.log(card_template.getElementById("Reserve_button".href));


		if(isquiet == false)
		{
			card_template.getElementById("bellicon").className = "bell icon";
			card_template.getElementById("bellicon").className = "bell slash icon";
		}

		if(rank == "1"){
		}else if(rank == "2"){
			card_template.getElementById("star3").style.display = 'none';
		}else if(rank == "3"){
			card_template.getElementById("star3").style.display = 'none';
			card_template.getElementById("star2").style.display = 'none';
		}else{
			card_template.getElementById("rank_icon").style.display = 'none';
		}

		//Append the library card under the library list
		S_list.appendChild(card_template)
	}
}


/************  Helper function: Library sort *************
*	Input: None
* Output: None
**************************************************/
function bubble_sort_helper(x){
	var swapp;
	var n = x.length - 1;
	do{
		swapp = false;
		for(var i = 0; i < n; i ++){
			if(parseInt(x[i].getElementsByClassName('chance')[0].innerText)
			< parseInt(x[i+1].getElementsByClassName('chance')[0].innerText)){
				var temp = x[i];
				x[i] = x[i+1];
				x[i+1] = temp;
				swapp = true;
			}
		}
		n--;
	}while (swapp);
	return x;
}



/********  Filter: Quick_Navigation_Bar ********
*	Input: None
* Output: None
**************************************************/

function reply_click(clicked_id){

		//Sort list by chance by default
		bubble_Sort();

		//Get reference to the list
		var list = document.getElementById("List_accordion");
		var children = list.childNodes;

		var listitem = [];
		for(var i = 0; i < children.length; i ++){
			if(children[i].nodeName == "DIV"){
				listitem.push(children[i]);
			}
		}

		//Block all the unnecessarry libraries
		for(var j = 0; j < listitem.length; j ++){
			if(listitem[j].id != clicked_id){
				listitem[j].style.display = "none";
			}else{
				listitem[j].style.display = "block";

			}
		}

}

function reportvalue(){
	var Library_filter = document.getElementById("Library_filter");
	var Chance_filter = document.getElementById("Chance_filter");
	console.log("reportvalue")

	console.log("Library_filter"+"    " +Library_filter.value)
	console.log("Chance_filter"+"    " +Chance_filter.value)

}

/************  Filtering Scenarios *************
*	Case 1: User don't care about library, only want to see by chance
		--> Click 'By Chance'
* Case 2: User wanna see by chance first, then want to see by library under by chance
		--> Click 'By Chance'  first, then Click 'By Library' second
* Case 3: User wanna see library directly, (we sort the library by chances as well by default)
		--> Click 'By Library' first, 'By Chance' clicked by default
* Case 4: After user click the Library, he wants to go back see chance-filtered only
		--> Unclick 'By Library', then click 'By Chance'
**************************************************/

/************  Sorting: Library sort *************
*	Input: None
* Output: None
**************************************************/
function library_Sort(){

	//If user's unclicking library_filter, automatically unclick chance filter as well
		// if user's clicking library filter, automatically click chance filter as well

		console.log("library sort")
		// get reference to the list
		var accordion = document.getElementById("List_accordion");
		var children = accordion.childNodes;

		// get all the cards
		var x = [];
		for(var j = 0; j < children.length; j ++){
			if(children[j].nodeName == "DIV"){
				x.push(children[j]);
			}
		}

		// Reset the visibility, if user uses quick navigation bar before
		for(var y = 0; y < x.length; y ++){
				x[y].style.display = "block";
		}

		var y = [];
		var gg = [];
		var main = [];
		var ugl = [];
		var chem = [];
		var aces = [];

		//Condition is useless because I change it to once user click
		//library filter, automatically turn on the chance filt


			for(var j = 0; j < x.length; j++){
				if(x[j].getElementsByClassName('libraryname')[0].innerText == "ACES Library"){
					aces.push(x[j]);
				}
			}
			if(aces.length != 0){
				aces = bubble_sort_helper(aces);
				for(var m = 0; m < aces.length; m++){
					y.push(aces[m]);
				}
			}else{
				console.log("no ACES Library found");
			}

			for(var j = 0; j < x.length; j++){
				if(x[j].getElementsByClassName('libraryname')[0].innerText == "Chemistry Library"){
					chem.push(x[j]);
				}
			}
			if(chem.length != 0){
				chem = bubble_sort_helper(chem);
				for(var m = 0; m < chem.length; m++){
					y.push(chem[m]);
				}
			}else{
				console.log("no Chemistry Library found");
			}

			for(var m = 0; m < x.length; m++){
				if(x[m].getElementsByClassName('libraryname')[0].innerText == "Grainger Library"){
					gg.push(x[m]);
				}
			}

			if(gg.length != 0){
				gg = bubble_sort_helper(gg);
				for(var m = 0; m < gg.length; m++){
					y.push(gg[m]);
				}
			}else{
				console.log("no Grainger Library found");
			}

			for(var i = 0; i < x.length; i++){
				if(x[i].getElementsByClassName('libraryname')[0].innerText == "Main Library"){
					main.push(x[i]);
				}
			}

			if(main.length != 0){
				main = bubble_sort_helper(main);
				for(var m = 0; m < main.length; m++){
					y.push(main[m]);
				}
			}else{
				console.log("no Main Library found");
			}

			for(var j = 0; j < x.length; j++){
				if(x[j].getElementsByClassName('libraryname')[0].innerText == "Undergraduate Library"){
					ugl.push(x[j]);
				}
			}
			if(ugl.length != 0){
				ugl = bubble_sort_helper(ugl);
				for(var m = 0; m < ugl.length; m++){
					y.push(ugl[m]);
				}
			}else{
				console.log("no Undergraduate Library found");
			}




		//Clear all Children
		while(accordion.hasChildNodes()){
			accordion.removeChild(accordion.lastChild);
		}

		//Append all sorted children
		for(var n = 0; n < y.length; n++){
			accordion.appendChild(y[n]);
		}

}

/************  Sorting: Bubble sort *************
*	Input: None
* Output: None
**************************************************/
function bubble_Sort(){

		//get reference to the list
		var accordion = document.getElementById("List_accordion");
		var children = accordion.childNodes;

		var x = [];
		for(var j = 0; j < children.length; j ++){
			if(children[j].nodeName == "DIV"){
				x.push(children[j]);
			}
		}

		// Reset the visibility in case user uses navigation bar before
		for(var y = 0; y < x.length; y ++){
				x[y].style.display = "block";
		}

		//Bubble sort algorithm
		var swapp;
		var n = x.length - 1;
		do{
			swapp = false;
			for(var i = 0; i < n; i ++){
				if(parseInt(x[i].getElementsByClassName('chance')[0].innerText)
				< parseInt(x[i+1].getElementsByClassName('chance')[0].innerText)){
					var temp = x[i];
					x[i] = x[i+1];
					x[i+1] = temp;
					swapp = true;
				}
			}
			n--;
		}while (swapp);

		//Clear all Children
		while(accordion.hasChildNodes()){
			accordion.removeChild(accordion.lastChild);
		}

		//Append all sorted children
		for(var n = 0; n < x.length; n++){
			accordion.appendChild(x[n]);
		}

}

/************  Sorting: Bubble sort 2***************
*	Input: None
* Output: None
**************************************************/
function bubble_Sort2(){

		//get reference to the list
		var accordion = document.getElementById("List_accordion");
		var children = accordion.childNodes;

		var x = [];
		for(var j = 0; j < children.length; j ++){
			if(children[j].nodeName == "DIV"){
				x.push(children[j]);
			}
		}

		// Reset the visibility in case user uses navigation bar before
		for(var y = 0; y < x.length; y ++){
				x[y].style.display = "block";
		}

		//Bubble sort algorithm
		var swapp;
		var n = x.length - 1;
		do{
			swapp = false;
			for(var i = 0; i < n; i ++){
				if(parseInt(x[i].getElementsByClassName('rank')[0].innerText)
				> parseInt(x[i+1].getElementsByClassName('rank')[0].innerText)){
					var temp = x[i];
					x[i] = x[i+1];
					x[i+1] = temp;
					swapp = true;
				}
			}
			n--;
		}while (swapp);

		//Clear all Children
		while(accordion.hasChildNodes()){
			accordion.removeChild(accordion.lastChild);
		}

		//Append all sorted children
		for(var n = 0; n < x.length; n++){
			accordion.appendChild(x[n]);
		}
}


jQuery(document).ready(function($)
{
$('#update')
	.popup({
		popup 	: '#myboxes',
		on		:	'click',
		closable: false,
		position:	'bottom right',
	});
})



// library data updates
jQuery(document).ready(function($)
{
  var toggle_name = "library";
  var display_name = "Library"
  var header_name = "Library"
  $("#"+toggle_name+"_wrap_toggle").click(function()
  {

    $("#"+toggle_name+"_wrap").slideToggle( "slow");

	  if ($("#"+toggle_name+"_wrap_toggle").text() == "Edit "+display_name+" Data")
      {
        $("#"+toggle_name+"_wrap_toggle").html("Hide "+display_name+" Data")
      }
	  else
      {
        $("#"+toggle_name+"_wrap_toggle").text("Edit "+display_name+" Data")
      }
  });

  $(".header"+header_name).click(function () {

      $header = $(this);
      //getting the next element
      $content = $header.next();
      //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
      $content.slideToggle(500, function () {
          //execute this after slideToggle is done
          //change text of header based on visibility of content div
          $header.text(function () {
              //change text based on condition
              return $content.is(":visible") ? "Cancel Add New "+display_name+" Entry" : "Add New "+display_name+" Entry";
          });
      });
  });

});

// Floor/section data updates
jQuery(document).ready(function($)
{
	var toggle_name = "floor";
	var display_name = "Floor/Section"
	var header_name = "Floor"
	$("#"+toggle_name+"_wrap_toggle").click(function()
	{

	  $("#"+toggle_name+"_wrap").slideToggle( "slow");

		if ($("#"+toggle_name+"_wrap_toggle").text() == "Edit "+display_name+" Data")
		{
		  $("#"+toggle_name+"_wrap_toggle").html("Hide "+display_name+" Data")
		}
		else
		{
		  $("#"+toggle_name+"_wrap_toggle").text("Edit "+display_name+" Data")
		}
	});

	$(".header"+header_name).click(function () {

		$header = $(this);
		//getting the next element
		$content = $header.next();
		//open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
		$content.slideToggle(500, function () {
			//execute this after slideToggle is done
			//change text of header based on visibility of content div
			$header.text(function () {
				//change text based on condition
				return $content.is(":visible") ? "Cancel Add New "+display_name+" Entry" : "Add New "+display_name+" Entry";
			});
		});
	});
});

// hoursOfOp data updates
jQuery(document).ready(function($)
{
	var toggle_name = "hours";
	var display_name = "Hours of Operation"
	var header_name = "Hours"
	$("#"+toggle_name+"_wrap_toggle").click(function()
	{

	  $("#"+toggle_name+"_wrap").slideToggle( "slow");

		if ($("#"+toggle_name+"_wrap_toggle").text() == "Edit "+display_name+" Data")
		{
		  $("#"+toggle_name+"_wrap_toggle").html("Hide "+display_name+" Data")
		}
		else
		{
		  $("#"+toggle_name+"_wrap_toggle").text("Edit "+display_name+" Data")
		}
	});

	$(".header"+header_name).click(function () {

		$header = $(this);
		//getting the next element
		$content = $header.next();
		//open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
		$content.slideToggle(500, function () {
			//execute this after slideToggle is done
			//change text of header based on visibility of content div
			$header.text(function () {
				//change text based on condition
				return $content.is(":visible") ? "Cancel Add New "+display_name+" Entry" : "Add New "+display_name+" Entry";
			});
		});
	});
});

// record data updates
jQuery(document).ready(function($)
{
	var toggle_name = "records";
	var display_name = "Records"
	var header_name = "records"
	$("#"+toggle_name+"_wrap_toggle").click(function()
	{

	  $("#"+toggle_name+"_wrap").slideToggle( "slow");

		if ($("#"+toggle_name+"_wrap_toggle").text() == "Edit "+display_name+" Data")
		{
		  $("#"+toggle_name+"_wrap_toggle").html("Hide "+display_name+" Data")
		}
		else
		{
		  $("#"+toggle_name+"_wrap_toggle").text("Edit "+display_name+" Data")
		}
	});

	$(".header"+header_name).click(function () {

		$header = $(this);
		//getting the next element
		$content = $header.next();
		//open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
		$content.slideToggle(500, function () {
			//execute this after slideToggle is done
			//change text of header based on visibility of content div
			$header.text(function () {
				//change text based on condition
				return $content.is(":visible") ? "Cancel Add New "+display_name+" Entry" : "Add New "+display_name+" Entry";
			});
		});
	});
});

// general functions
jQuery(document).ready(function($)
{
	$(".showHideCard").click(function () {

		$header = $(this);
		//getting the next element
		$content = $header.next();
		//open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
		$content.slideToggle(500, function () {
			//execute this after slideToggle is done
			//change text of header based on visibility of content div
			$header.text(function () {
			});
		});

	});
});

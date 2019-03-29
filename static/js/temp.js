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
}else{
    console.log('Library not defined')
}

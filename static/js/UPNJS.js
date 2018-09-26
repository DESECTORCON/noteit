function my_notes_sidebar_site_hidden() {
    $('#MAINDIV').hide();
    if( document.getElementById("file").files.length == 0 ){
        console.log("upload started");
        alert('Saving your note. Please wait');
    }

    var x = document.getElementById("myDIV");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
    $(document).ready(function() {
       $('#myDIV').hide();
    });

}
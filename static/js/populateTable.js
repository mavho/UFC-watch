function get_payload(){
    // load search result data
    var data_req = new XMLHttpRequest();
    var text_req;
    //data_req.overrideMimeType("application/json");
    //api call
    data_req.open("GET", "http://homaverick.pythonanywhere.com/api/predictions", true);

    data_req.onreadystatechange = function(){
        if(data_req.readyState == 4 && data_req.status == 200){
            text_req = data_req.responseText;
            var actual_JSON = JSON.parse(text_req);
            console.log(actual_JSON)

            tabulate(actual_JSON)
            
        }
    }
    data_req.send();
    
    return text_req;
}
function test_table() {
    test_obj='{"bouts":[{"Loser":"Glover Teixeira","Winner":"Anthony Smith"},{"Loser":"Shamil Gamzatov","Winner":"Ovince Saint Preux"},{"Loser":"Cynthia Calvillo","Winner":"Antonina Shevchenko"},{"Loser":"Matt Frevola","Winner":"Roosevelt Roberts"},{"Loser":"Michael Johnson","Winner":"Evan Dunham"},{"Loser":"Ariane Carnelossi","Winner":"Mackenzie Dern"},{"Loser":"Andrew Sanchez","Winner":"Zak Cummings"},{"Loser":"Raphael Pessoa","Winner":"Alexander Romanov"},{"Loser":"David Zawada","Winner":"Anthony Rocco Martin"},{"Loser":"Alan Patrick","Winner":"Christos Giagos"},{"Loser":"Billy Quarantillo","Winner":"Gavin Tucker"}],"event":"UFC Fight Night: Smith vs. Teixeira"}'
    var actual_JSON = JSON.parse(test_obj);
    console.log(actual_JSON)
    tabulate(actual_JSON)
}

function tabulate(data){
    var fight_table = document.getElementById('fight_table')

    var event_header = document.getElementById('header')
        event_header.className="title has-text-weight-bold has-text-grey"
        event_header.innerHTML = data['event'] + " Predictions"


    for(var i in data['bouts']){
        var listing   = document.createElement("div") 
            listing.className = "tile level"
            listing.id="fight-listing"

        var wrapper1 = document.createElement("div")
            wrapper1.className="tile is-parent"
        
        var fighter1 = document.createElement("div")
            fighter1.className="tile box is-child has-text-weight-bold has-background-success has-text-black"
            fighter1.id="fighter1"
            fighter1.innerHTML=data['bouts'][i]['Winner']

        wrapper1.appendChild(fighter1)
        var wrapper2= document.createElement("div")
            wrapper2.className="tile is-parent"
        var fighter2 = document.createElement("div")
            fighter2.className="tile box is-child has-text-weight-bold has-background-danger has-text-black"
            fighter2.id="fighter2"
            fighter2.innerHTML=data['bouts'][i]['Loser']
        wrapper2.appendChild(fighter2)

        var wrapper3 = document.createElement("div")
            wrapper3.className="tile is-parent is-1"

        var icon_container = document.createElement("span")
            icon_container.className = "icon tile is-child has-text-white has-text-centered"
        var icon = document.createElement("i")
            icon.className="fas fa-3x fa-fist-raised"

        icon_container.appendChild(icon)
        wrapper3.appendChild(icon_container)

        listing.appendChild(wrapper1)
        listing.append(wrapper3)

        listing.appendChild(wrapper2)
        fight_table.appendChild(listing)
    }
}
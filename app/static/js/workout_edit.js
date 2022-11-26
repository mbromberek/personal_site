function copyNotes(){
    console.log("Copy Notes +");
    var clothesEle = document.getElementById('workout_clothes');
    var clothesVal = '';
    if (clothesEle != null){
        clothesVal = clothesEle.innerHTML;
    }
    // console.log(clothesVal);

    var notesEle = document.getElementById('workout_notes');
    var notesVal = '';
    if (notesEle != null){
        notesVal = notesEle.innerHTML.replaceAll('\<br\>','\n').trim();
    }
    // console.log(notesVal);

    var wthrStrtEle = document.getElementById('workout_weather_start');
    var wthrStrtVal = '';
    if (wthrStrtEle != null){
        // Convert 2 or more spaces between words into single space
        wthrStrtVal = wthrStrtEle.innerHTML.replace(/\s{2,}/g,' ').trim();
    }
    // console.log(wthrStrtVal);

    var wthrEndEle = document.getElementById('workout_weather_end');
    var wthrEndVal = '';
    if (wthrEndEle != null){
        wthrEndVal = wthrEndEle.innerHTML.replace(/\s{2,}/g,' ').trim();
    }
    // console.log(wthrEndVal);

    combinedNotes = wthrStrtVal + '\n' +
        wthrEndVal + '\n' +
        clothesVal + '\n' +
        notesVal;
    // console.log(combinedNotes);

    navigator.clipboard.writeText(combinedNotes);

}

async function pasteNotes(){
    console.log("Paste Notes");

    var clothesEle = document.getElementById('clothes');
    var notesEle = document.getElementById('notes');
    const clothesPattern = /(Shorts|Tights)(.{0,125}?)(\.|\n)/g;


    // navigator.clipboard.readText().then(text => clothesNotesTxt = text);
    // clothesNotesTxt = document.execCommand("paste");
    try {
        const clothesNotesTxt = await navigator.clipboard.readText();
        console.log('Pasted content: ', clothesNotesTxt);

        // var matchClothes = re.search(clothesPattern,rec, flags=re.IGNORECASE)
        var matchClothes = clothesNotesTxt.match(clothesPattern);
        var clothesLen = 0;
        console.log('match Clothes: ', matchClothes);

        if (clothesEle != null && matchClothes.length >0){
            clothesEle.value = matchClothes[0];
            clothesLen = matchClothes[0].length;
        }
        if (notesEle != null){
            if (notesEle.value == null || notesEle.value == ''){
                notesEle.value = clothesNotesTxt.substr(clothesLen).trim();
            }else{
                notesEle.value = clothesNotesTxt.substr(clothesLen).trim() + '\n' + notesEle.value;
            }
        }
        document.getElementById('alert_div').innerHTML = 'Data Pasted!';
        document.getElementById('alert_div').style.display = 'inline-block';
    } catch (err) {
      console.error('Failed to read clipboard contents: ', err);
      // window.alert('Failed to read clipboard contents');
      document.getElementById('alert_div').innerHTML = 'Failed to read clipboard contents';
      document.getElementById('alert_div').style.display = 'inline-block';
      document.getElementById('alert_div').style.backgroundColor = '#ff2233';
    }

}

function split_intrvl(sel_ele, wrkt_id, intrvl_id){
    // alert("split_interval: " + wrkt_id + " " + intrvl_id);
    console.log("split_intrvl: " + wrkt_id + " " + intrvl_id);

    let sel_row = sel_ele.parentElement;
    sel_row.style.backgroundColor = 'lightgray';
    split_dist = sel_row.querySelector('[id$="split_dist"]').value;
    split_dur = '';
    console.log('New Distance: ' + split_dist);

    // Perform AJAX call passing the workout id, interval id, and new distance
    $.get('/split_intrvl', {
        wrkt_id: wrkt_id,
        intrvl_id: intrvl_id,
        split_dist: split_dist,
        split_dur: split_dur
    }).done(function(response){
        show_split(response);
    }).fail(function(){
        console.error("Error: Could not contact server.");
    })
    ;
}

function show_split(response){
    console.log('show_split');
    console.log(response);
    let intrvl_id = response['intrvl_id'];
    let rowId_1 = 'row_'+intrvl_id+'_1'
    let rowId_2 = 'row_'+intrvl_id+'_2'
    let lap_1 = response['laps'][0]
    let lap_2 = response['laps'][1]

    let row_updt = document.querySelector('#'+rowId_1);
    console.log(row_updt);
    // row_updt = document.getElementById(rowId);
    row_updt.style='display:inline-flex;color:blue;background-color:yellow;';
    row_updt.querySelector('#dist').innerHTML = lap_1['dist_mi'];
    row_updt.querySelector('#dur').innerHTML = lap_1['dur_str'];
    row_updt.querySelector('#hr').innerHTML = lap_1['hr'];
    row_updt.querySelector('#ele_up').innerHTML = lap_1['ele_up'];
    row_updt.querySelector('#ele_down').innerHTML = lap_1['ele_down'];

    row_updt = document.querySelector('#'+rowId_2);
    row_updt.style='display:inline-flex;color:blue;background-color:yellow;';
    row_updt.querySelector('#dist').innerHTML = lap_2['dist_mi'];
    row_updt.querySelector('#dur').innerHTML = lap_2['dur_str'];
    row_updt.querySelector('#hr').innerHTML = lap_2['hr'];
    row_updt.querySelector('#ele_up').innerHTML = lap_2['ele_up'];
    row_updt.querySelector('#ele_down').innerHTML = lap_2['ele_down'];

}
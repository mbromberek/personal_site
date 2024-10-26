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
        // notesVal = notesEle.innerHTML.replaceAll('\<br\>','\n').trim();
        notesVal = notesEle.innerHTML.replaceAll('\<br\>','').trim();
    }

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

function validate_data(){
    console.log("validate_data");
    let intrvl_rows = document.querySelectorAll('[id^=orig_intrvl_row_');
    console.log(intrvl_rows);
    intrvl_split_lst = [];
    for (i=0; i<intrvl_rows.length; i++){
        let intrvl = intrvl_rows[i];
        let split_dist = intrvl.querySelector('[id$="split_dist"]').value;
        let orig_dist = parseFloat(intrvl.querySelector('#dist').innerHTML);
        if (split_dist != ''){
            if (isNaN(split_dist)){
                alert('Split Distance ('+ split_dist + ') needs to be a number smaller than intervals distance.');
                return false;
            }
            if (split_dist >= orig_dist){
                alert('Split Distance ('+ split_dist + ') needs to be smaller than intervals distance (' + orig_dist + ').');
                return false;
            }
        }
    }
    return true;
}

function preview_split_intrvl(wrkt_id){
    console.log("preview_split_intrvl");
    let intrvl_rows = document.querySelectorAll('[id^=orig_intrvl_row_');
    console.log(intrvl_rows);
    intrvl_split_lst = [];
    let merge_next_lap = false;
    let merge_laps = false;
    for (i=0; i<intrvl_rows.length; i++){
        let intrvl = intrvl_rows[i];
        let split_intrvl_id = intrvl.querySelector('[id$="wrkt_intrvl_id"]').value;
        let split_dist = intrvl.querySelector('[id$="split_dist"]').value;
        let orig_dist = parseFloat(intrvl.querySelector('#dist').innerHTML);
        if (i+1 < intrvl_rows.length ){
            merge_laps = intrvl.querySelector('[id$="merge_laps_chk"]').checked;
        }else{
            // Last row does not have a merge checkbox so set it to false
            merge_laps = false;
        }
        if (merge_laps == true){
            //Else IF Merge is selected
            console.log('id: ' + split_intrvl_id + ' merge with lap below it');
            intrvl_split_lst.push({'id':split_intrvl_id, 'merge':true});
            intrvl.style.backgroundColor = 'lightgray';
            merge_next_lap = true;
        }else if (merge_next_lap == true){
            merge_next_lap = false;
            intrvl.style.backgroundColor = 'lightgray';
        } else if (split_dist != ''){
            if (isNaN(split_dist)){
                alert('Split Distance ('+ split_dist + ') needs to be a number smaller than intervals distance.');
                return;
            }
            if (split_dist >= orig_dist){
                alert('Split Distance ('+ split_dist + ') needs to be smaller than intervals distance (' + orig_dist + ').');
                return;
            }
            console.log('id: ' + split_intrvl_id + ' split_dist: ' + split_dist);
            intrvl_split_lst.push({'id':split_intrvl_id, 'split_dist':split_dist});
            intrvl.style.backgroundColor = 'lightgray';
            //Will ignore Merge if the Split Dist is filled in so set merge to False
        }
    }
    console.log(intrvl_split_lst);
    $.get('/split_intrvl', {
        'wrkt_id': wrkt_id,
        'intrvl_split_lst': JSON.stringify(intrvl_split_lst)
    }).done(function(response){
        show_split(response);
    }).fail(function(response){
        console.error("Error: Could not contact server.");
    })
    ;

}

function show_split(response){
    console.log('show_split');
    console.log(response);

    // interval_change = {};
    split_laps = response['split_laps']
    
    for (i=0; i<split_laps.length; i++){
        split_lap = split_laps[i];
        let intrvl_id = split_lap['intrvl_id'];
        let rowId_1 = 'row_'+intrvl_id+'_1'
        let rowId_2 = 'row_'+intrvl_id+'_2'
        let lap_1 = split_lap['laps'][0]
    
        let row_updt = document.querySelector('#'+rowId_1);
        console.log(row_updt);
        // row_updt = document.getElementById(rowId);
        row_updt.style='display:inline-flex;color:blue;background-color:yellow;';
        row_updt.querySelector('#dist').innerHTML = lap_1['dist_mi'];
        row_updt.querySelector('#dur').innerHTML = lap_1['dur_str'];
        row_updt.querySelector('#hr').innerHTML = lap_1['hr'];
        row_updt.querySelector('#ele_up').innerHTML = lap_1['ele_up'];
        row_updt.querySelector('#ele_down').innerHTML = lap_1['ele_down'];
    
        if (split_lap['laps'].length >1){
            let lap_2 = split_lap['laps'][1]
            row_updt = document.querySelector('#'+rowId_2);
            row_updt.style='display:inline-flex;color:blue;background-color:yellow;';
            row_updt.querySelector('#dist').innerHTML = lap_2['dist_mi'];
            row_updt.querySelector('#dur').innerHTML = lap_2['dur_str'];
            row_updt.querySelector('#hr').innerHTML = lap_2['hr'];
            row_updt.querySelector('#ele_up').innerHTML = lap_2['ele_up'];
            row_updt.querySelector('#ele_down').innerHTML = lap_2['ele_down'];
        }else{
            row_updt.querySelector('#updt_rec_msg').innerHTML = 'New Merged Record';
        }
    }


}

function edit_workout_tags(wrkt_id){
    console.log('edit_workout_tags');
    $('#tagSelectModal').modal('show');
    let wrkt_edit_tags_ele = document.getElementById('workout_edit_tags_body');
    wrkt_edit_tags_ele.innerHTML = "<div style='width:100%;align:center;'><img src='static/images/loading.gif' /></div>";
    
    //Make API call to get list of workouts
    $.get('/get_workout_tags', {
        'wrkt_id': wrkt_id
    }).done(function(response){
        show_workout_edit_tags(response);
        
    }).fail(function(response){
        console.error("Error: Could not contact server.");
    })
    ;
}

function show_workout_edit_tags(response){
    console.log('show_workout_edit_tags');
    console.log(response);
    $('#tagSelectModal').modal('show');
    
    let wrkt_edit_tags_ele = document.getElementById('workout_edit_tags_body');
    wrkt_edit_tags_ele.innerHTML = "";
    for (let i=0; i<response['items'].length; i++){
        let tag = response['items'][i]
        template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
        
        template_clone.querySelector("#tag_id").innerHTML = tag['id'];
        template_clone.querySelector("#tag_chk").checked = tag['on_workout'];
        template_clone.querySelector("#tag_nm").innerHTML = tag['nm'];
        template_clone.querySelector("#usage_count").innerHTML = tag['usage_count'];
        
        wrkt_edit_tags_ele.appendChild(template_clone);
    }
}

function save_workout_tag_edits(wrkt_id){
    console.log('save_workout_tag_edits')
    console.log(wrkt_id);
    
    let wrkt_edit_tags_ele = document.getElementById('workout_edit_tags_body');
    let wrkt_tags_div = wrkt_edit_tags_ele.getElementsByTagName('div');
    let tag_id_lst = [];
    for (let i=0; i<wrkt_tags_div.length; i++){
        if (wrkt_tags_div[i].querySelector('#tag_chk').checked == true){
            tag_id_lst.push(wrkt_tags_div[i].querySelector('#tag_id').innerHTML);
        }
        /*let tag = {
            'tag_id':wrkt_tags_div[i].querySelector('#tag_id').innerHTML,
            'tag_nm' : wrkt_tags_div[i].querySelector('#tag_nm').innerHTML,
            'tag_chk' : wrkt_tags_div[i].querySelector('#tag_chk').checked
        };*/
        // let tag_id = wrkt_tags_div[i].querySelector('#tag_id').innerHTML;
        // let tag_nm = wrkt_tags_div[i].querySelector('#tag_nm').innerHTML;
        // let tag_chk = wrkt_tags_div[i].querySelector('#tag_chk').checked;
        // console.log('Tag:' + tag_id + ' name: ' + tag_nm + ' checked: ' + tag_chk);
        // console.log(tag);
        // tags.push(tag);
    }
    console.log(tag_id_lst);
    
    $('#tagSelectModal').modal('hide');
    //Make API call to get list of workouts
    $.post('/update_workout_tags', {
        'wrkt_id': wrkt_id, 'tags':JSON.stringify(tag_id_lst)
    }).done(function(response){
        // show_workout_edit_tags(response);
        console.log("Success update_workout_tags");
        // console.log(response['items']);
        location.reload();
        
    }).fail(function(response){
        console.error("Error: Could not contact server.");
    })
    ;
}



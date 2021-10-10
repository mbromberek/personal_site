/*
*/
// function wrktSearchBtn(){
//     console.log("wrktSearchBtn")
//
//     var urlOrig = window.location.href;
//     var urlNoParm = urlOrig.split('?')[0];
//     var urlParmDict = brkdUrlParms(urlOrig.split('?')[1]);
//
//     // alert(document.getElementById('clear_filter_btn').clicked);
//     var txtSearch = document.getElementById("text_search").value;
//     var strtTempSearch = document.getElementById("strt_temp_search").value;
//     var distSearch = document.getElementById("distance_search").value;
//
//     //Update URL fields with values from search fields
//     if (txtSearch != ''){
//         urlParmDict['text_search'] = txtSearch;
//     }else{
//         delete urlParmDict['text_search'];
//     }
//     if (strtTempSearch != ''){
//         urlParmDict['temperature'] = strtTempSearch;
//     }else{
//         delete urlParmDict['temperature'];
//     }
//     if (distSearch != ''){
//         urlParmDict['distance'] = distSearch;
//     }else{
//         delete urlParmDict['distance'];
//     }
//     delete urlParmDict['page'];
//     var urlParmNew = generateUrlParms(urlParmDict);
//
//     console.log(urlNoParm + '?' + urlParmNew);
//     window.location.href = urlNoParm + '?' + urlParmNew;
// }

/*
Convert passed String of URL parameters in parmStr to a
dictionary of the parameters. Returns the parameters dictionary.
}
*/
function brkdUrlParms(parmStr){
    var parmDict = {};
    var parmKey;
    var parmVal;
    if (parmStr == null || parmStr == ''){
        return parmDict;
    }
    console.log('parmStr: ' + parmStr);
    var parmLst = parmStr.split('&');
    console.log('parmLst: ' + parmLst);
    for (var parm in parmLst){
        console.log(parmLst[parm]);
        parmSplit = parmLst[parm].split('=');
        parmKey = parmSplit[0];
        console.log('key:'+parmKey);
        if (parmKey != '' && parmSplit.length>1 && parmSplit[1] != ''){
            parmVal = parmSplit[1];
            parmDict[parmKey] = parmVal;
        }
    }
    return parmDict
}

/*
Convert passed in dictionary of parameters in parmDict to a
string of the parameters in the format for a URL
*/
function generateUrlParms(parmDict){
    var parmStr = '';
    for (var parmKey in parmDict) {
        if (parmStr != ''){
            parmStr += '&'
        }
        parmStr += parmKey + '=' + parmDict[parmKey];
    }
    return parmStr;
}

/*
Hides and shows the search area of workouts page
*/
function filterToggle(element){
    ele = document.getElementById("show_hide_filter_btn");
    $('#extra_filter_fields').collapse('toggle')
        .on('shown.bs.collapse', function(){
            // console.log('shown');
            ele.setAttribute('value', 'Hide Search');
        })
        .on('hidden.bs.collapse', function(){
            // console.log('hide');
            ele.setAttribute('value', 'Show Search');
        });
}

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
                notesEle.value = clothesNotesTxt.substr(clothesLen).trim() + '\n' + notesEle.value;
            }else{
                notesEle.value = clothesNotesTxt.substr(clothesLen).trim();
            }
        }


    } catch (err) {
      console.error('Failed to read clipboard contents: ', err);
    }

}

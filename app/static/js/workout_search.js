let extraFiltersVisible = false;

/*
*/
function wrktSearchBtn(){
    var txtSearch = document.getElementById("text_search").value;
    var strtTempSearch = document.getElementById("strt_temp_search").value;
    var distSearch = document.getElementById("distance_search").value;

    var urlOrig = window.location.href;
    var urlNoParm = urlOrig.split('?')[0];
    var urlParmDict = brkdUrlParms(urlOrig.split('?')[1]);
    //Update URL fields with values from search fields
    if (txtSearch != ''){
        urlParmDict['text_search'] = txtSearch;
    }else{
        delete urlParmDict['text_search'];
    }
    if (strtTempSearch != ''){
        urlParmDict['temperature'] = strtTempSearch;
    }else{
        delete urlParmDict['temperature'];
    }
    if (distSearch != ''){
        urlParmDict['distance'] = distSearch;
    }else{
        delete urlParmDict['distance'];
    }
    delete urlParmDict['page'];
    var urlParmNew = generateUrlParms(urlParmDict);

    console.log(urlNoParm + '?' + urlParmNew);
    window.location.href = urlNoParm + '?' + urlParmNew;
}

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
Uses hardcoded URL paths so that could cause an issue instead of using
url_for
*/
function hoverFilterToggle(element){
    ele = document.getElementById("filter_toggle_img");
    ele.setAttribute('src', '/static/images/icons8-filter-50-onhover.png');
}
/*
*/
function unHoverFilterToggle(element){
    ele = document.getElementById("filter_toggle_img");
    if (extraFiltersVisible == true){
        ele.setAttribute('src', '/static/images/icons8-filter-50-selected.png');
    }else{
        ele.setAttribute('src', '/static/images/icons8-filter-50.png');
    }
}
/*
*/
function filterToggleOld(element){
    console.log('filterToggle');
    ele = document.getElementById("show_hide_filter_btn");
    extra_filter_fields = document.getElementById("extra_filter_fields");
    // console.log(extra_filter_fields.getAttribute('class'))
    searchFieldsClasses = extra_filter_fields.getAttribute('class')
    // ele.style.display = 'block';
    // $('.collapse').collapse('toggle');
    // $('#extra_filter_fields').collapse('toggle');

    // if (searchFieldsClasses.includes('collapse')){
    var isExpanded = $('#extra_filter_fields').attr("aria-expanded");
    console.log('Initial:' + isExpanded);
    if (isExpanded){
        extraFiltersVisible = true;
        $('#extra_filter_fields').collapse('show');
        ele.setAttribute('value', 'Hide Search');
    }else{
        extraFiltersVisible = false;
        $('#extra_filter_fields').collapse('hide');
        // ele.setAttribute('src', '/static/images/icons8-filter-50.png');
        ele.setAttribute('value', 'Show Search');
    }
    // console.log(extraFiltersVisible);
    // console.log(extra_filter_fields.getAttribute('class'))
    console.log('end:' + isExpanded);
    shown.bs.collapse
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

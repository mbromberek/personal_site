let nextPage = 2;
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

/*
function showDownload(element){
    console.log("showDownload");
    var ele = document.getElementById("csv_download_specs");
    console.log(ele.innerHTML);
    document.getElementById("csv_download_specs").style.display = 'block'
    console.log(ele.style.display);
}
*/

function getNextWrkts(filter){
    console.log("getNextWrkts");
    console.log(filter);
    $.get('/more_workouts', {
        type: filter['type'],
        category: filter['category'],
        distance: filter['distance'],
        end_dt: filter['end_dt'],
        max_dist: filter['max_dist'],
        max_strt_temp: filter['max_strt_temp'],
        min_dist: filter['min_dist'],
        min_strt_temp: filter['min_strt_temp'],
        page: nextPage,
        strt_dt: filter['strt_dt'],
        temperature: filter['temperature'],
        text_search: filter['text_search']

    }).done(function(response){
        loadItems(response);
    }).fail(function(){
        console.error("Error: Could not contact server.");
    })
    ;

}

function formatDate(date_str) {
    let d = new Date(date_str);
    let year = d.getUTCFullYear();
    let month = (d.getUTCMonth() + 1).toString().padStart(2,'0');
    let day = d.getUTCDate().toString().padStart(2,'0');
    dt = [year, month, day].join('-');

    let hour = d.getUTCHours().toString().padStart(2,'0');
    let minute = d.getUTCMinutes().toString().padStart(2,'0');
    let second = d.getUTCSeconds().toString().padStart(2,'0');
    return dt + ' ' + hour + ':' + minute;
}

function loadItems(response){
    console.log(response);

    let wrkts = response['workouts'];
    let wrkt_lst_ele = document.getElementById('wrkt_lst');
    for (var i=0; i<wrkts.length; i++){
        let wrkt_dttm_formatted = formatDate(wrkts[i]['wrkt_dttm']);

        let template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
        template_clone.querySelector("#wrkt_lnk").innerHTML = wrkt_dttm_formatted + ' - ' + wrkts[i]['type'];
        template_clone.querySelector("#wrkt_lnk").href = wrkts[i]['_links']['self'];
        template_clone.querySelector("#wrkt_edit_lnk").href = wrkts[i]['_links']['edit'];

        template_clone.querySelector("#category_training_loc").innerHTML = wrkts[i]['category_training_loc'];

        if (wrkts[i]['_links'].hasOwnProperty('map_thumb')){
            template_clone.querySelector("#map_thumb").innerHTML = '<img src="'+ wrkts[i]['_links']['map_thumb'] +'" style="width:100%; height:auto;" >';
        }
        template_clone.querySelector("#distance").innerHTML = wrkts[i]['dist_mi'];
        template_clone.querySelector("#duration").innerHTML = wrkts[i]['duration'];
        template_clone.querySelector("#pace").innerHTML = wrkts[i]['pace'] + ' ' + wrkts[i]['pace_uom'];

        if (wrkts[i]['clothes'] != ''){
            template_clone.querySelector("#clothes").innerHTML = 'Wore: ' +  wrkts[i]['clothes'];
        }
        template_clone.querySelector("#gear").innerHTML = wrkts[i]['gear'];
        if (wrkts[i]['notes_summary'] != ''){
            template_clone.querySelector("#notes").innerHTML = 'Notes: ' +  wrkts[i]['notes_summary'];
        }

        let weather_start = wrkts[i]['weather_start'];
        if (weather_start['temp'] == '' || isNaN(weather_start['temp']) ){
            template_clone.querySelector("#weather_start").innerHTML = '';
        }else{
            template_clone.querySelector("#weather_start_temp").innerHTML = Math.round(weather_start['temp']) + '&#176';
            if (weather_start['wethr_cond'] != ''){
                template_clone.querySelector("#weather_start_cond").innerHTML = '&nbsp;' + weather_start['wethr_cond'];
            }
            if (weather_start['hmdty'] != '' && !isNaN(weather_start['hmdty'])){
                template_clone.querySelector("#weather_start_hmdty").innerHTML = ', ' + Math.round(weather_start['hmdty']) + '%hy';
            }
            if (weather_start['dew_point'] != '' && !isNaN(weather_start['dew_point'])){
                template_clone.querySelector("#weather_start_dew_pt").innerHTML = ', dew point ' + Math.round(weather_start['dew_point']) + '&#176';
            }
            if (weather_start['temp_feels_like'] != '' && !isNaN(weather_start['temp_feels_like'])){
                template_clone.querySelector("#weather_start_feels").innerHTML = ', feels ' + Math.round(weather_start['temp_feels_like']);
            }
            if (weather_start['wind_speed'] != '' && !isNaN(weather_start['wind_speed'])){
                template_clone.querySelector("#weather_start_wind_speed").innerHTML = ', wind speed ' + Math.round(weather_start['wind_speed']) + 'mph';
            }
            if (weather_start['wind_gust'] != '' && !isNaN(weather_start['wind_gust'])){
                template_clone.querySelector("#weather_start_wind_gust").innerHTML = ', gust ' + Math.round(weather_start['wind_gust']);
            }
        }
        let weather_end = wrkts[i]['weather_end'];
        if (weather_end['temp'] == '' || isNaN(weather_end['temp']) ){
            template_clone.querySelector("#weather_end").innerHTML = '';
        }else{
            template_clone.querySelector("#weather_end_temp").innerHTML = Math.round(weather_end['temp']) + '&#176';
            if (weather_end['wethr_cond'] != ''){
                template_clone.querySelector("#weather_end_cond").innerHTML = '&nbsp;' + weather_end['wethr_cond'];
            }
            if (weather_end['hmdty'] != '' && !isNaN(weather_end['hmdty'])){
                template_clone.querySelector("#weather_end_hmdty").innerHTML = ', ' + Math.round(weather_end['hmdty']) + '%hy';
            }
            if (weather_end['dew_point'] != '' && !isNaN(weather_end['dew_point'])){
                template_clone.querySelector("#weather_end_dew_pt").innerHTML = ', dew point ' + Math.round(weather_end['dew_point']) + '&#176';
            }
            if (weather_end['temp_feels_like'] != '' && !isNaN(weather_end['temp_feels_like'])){
                template_clone.querySelector("#weather_end_feels").innerHTML = ', feels ' + Math.round(weather_end['temp_feels_like']);
            }
            if (weather_end['wind_speed'] != '' && !isNaN(weather_end['wind_speed'])){
                template_clone.querySelector("#weather_end_wind_speed").innerHTML = ', wind speed ' + Math.round(weather_end['wind_speed']) + 'mph';
            }
            if (weather_end['wind_gust'] != '' && !isNaN(weather_end['wind_gust'])){
                template_clone.querySelector("#weather_end_wind_gust").innerHTML = ', gust ' + Math.round(weather_end['wind_gust']);
            }
        }


        //Need to determine how to handle calculating this and make it work for mobile too
        template_clone.querySelector("#wrkt_card").style.height = '300px';

        wrkt_lst_ele.appendChild(template_clone);
    }
    nextPage = response['page'];
    //TODO if nextPage is null means no more records, need to make button disabled
}

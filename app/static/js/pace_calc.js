//List of cookies being saved for different values
var calcPaceFormLst = [];
var calcTimeFormLst = [];
var calcDistFormLst = [];
var calcAdjPaceFormLst = [];

//Number of days to save cookies for
var cookieExpireDays = 60;
var paceFormCt = 0;
var timeFormCt = 0;
var distFormCt = 0;
var adjPaceFormCt = 0;

/*
Run when calculate button is pressed for getting pace
Saves fields as cookies if they are populated and Remember Calculations is checked
*/
function calcPaceBtn(formId){
    // console.log(formId);
    let form_ele = document.getElementById(formId);

    let h = form_ele.querySelector("#cp_time_h").value;
    let m = form_ele.querySelector("#cp_time_m").value;
    let s = form_ele.querySelector("#cp_time_s").value;
    let dist = form_ele.querySelector("#cp_distance").value;
    if (!(calcPaceFormLst.includes(formId))) {
        calcPaceFormLst.push(formId);
    }
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie(formId + "_calcPaceHours", h, cookieExpireDays);
        setCookie(formId + "_calcPaceMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcPaceSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcPaceDistance", dist, cookieExpireDays);
        setCookie("calcPaceFormLst", String(calcPaceFormLst), cookieExpireDays)
    }

    form_ele.querySelector("#cp_pace").value = sec_to_time_str(calcPace(h,m,s,dist));
}

/*
Calculate Pace using the passed in distance and time
Converts hours, minutes, seconds to seconds and sums together
Pace = Time in Seconds / Distance
*/
function calcPace(h, m, s, dist){
    var time_sec = time_to_sec(h, m, s)
    var pace_sec = Math.round(time_sec / dist);
    return pace_sec;
}

/*
Run when calculate button is pressed for getting time
Saves fields as cookies if they are populated and Remember Calculations is checked
*/
function calcTimeBtn(formId){
    // console.log(formId);
    let form_ele = document.getElementById(formId);

    let m = form_ele.querySelector("#ct_pace_m").value;
    let s = form_ele.querySelector("#ct_pace_s").value;
    let dist = form_ele.querySelector("#ct_distance").value;
    if (!(calcTimeFormLst.includes(formId))) {
        calcTimeFormLst.push(formId);
    }

    if (dist != '' && document.getElementById("save_cookie").checked){
        // setCookie(formId + "_calcPaceHours", h, cookieExpireDays);
        setCookie(formId + "_calcTimeMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcTimeSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcTimeDistance", dist, cookieExpireDays);
        setCookie("calcTimeFormLst", String(calcTimeFormLst), cookieExpireDays)
    }
    form_ele.querySelector("#ct_time").value = sec_to_time_str(calcTime(0,m,s,dist));
}

/*
Calculate Time using the passed in pace times and distance
Converts the pace hours minutes and seconds to seconds and sums together
Time = Pace in Seconds * Distance
*/
function calcTime(h, m, s, dist){
    var pace_sec = time_to_sec(h, m, s)
    var time_sec = pace_sec * dist;
    return time_sec;
}

/*
Calculate Adjusted Pace based on temperature and desired pace
Converts the pace minutes and seconds to seconds and sums together
Adjusted Pace = Pace in Seconds + ((temperature - 59) / 1.8) * 4.5)
*/
function calcAdjPaceBtn(formId){
    // console.log(formId);
    let form_ele = document.getElementById(formId);

    let m = form_ele.querySelector("#pace_m").value;
    let s = form_ele.querySelector("#pace_s").value;
    let temperature = form_ele.querySelector("#temperature").value;
    if (!(calcAdjPaceFormLst.includes(formId))) {
        calcAdjPaceFormLst.push(formId);
    }

    if (temperature != '' && document.getElementById("save_cookie").checked){
        setCookie(formId + "_calcAdjPaceMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcAdjPaceSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcAdjPaceTemperature", temperature, cookieExpireDays);
        setCookie("calcAdjPaceFormLst", String(calcAdjPaceFormLst), cookieExpireDays)
    }
    form_ele.querySelector("#adjusted_pace").value = sec_to_time_str(calcAdjPace(0, m, s, temperature), 'ms');
}

function calcAdjPace(h, m, s, temp){
    //calculate pace normal way
    pace_sec = time_to_sec(h, m, s);

    //if temp is <= 59 degrees fahrenheit then return pace with no adjustment
    if (temp <= 59){
        return pace_sec
    }else{
        //increase_per_mile_seconds = ( (temperature - 59) / 1.8) * 4.5
        increase_per_mile_seconds = ( (temp - 59) / 1.8) * 4.5
        return pace_sec+increase_per_mile_seconds
    }

}

/*
Run when calculate button is pressed for getting distance
Saves fields as cookies if they are populated and Remember Calculations is checked
*/
function calcDistBtn(formId){
    form_ele = document.getElementById(formId);
    let tm_h = form_ele.querySelector("#time_h").value;
    let tm_m = form_ele.querySelector("#time_m").value;
    let tm_s = form_ele.querySelector("#time_s").value;
    let pace_m = form_ele.querySelector("#pace_m").value;
    let pace_s = form_ele.querySelector("#pace_s").value;
    let dist = '';

    //Need at least one value for time or pace
    if ((tm_h != '' || tm_m != '' || tm_s != '') || (pace_m != '' || pace_s != '')) {
        dist = calcDistance(tm_h, tm_m, tm_s, 0, pace_m, pace_s);
    }else{
        alert('Please enter a value for Time and Pace')
    }

    if (!(calcDistFormLst.includes(formId))) {
        calcDistFormLst.push(formId);
    }


    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie(formId + "_calcDistTmHours", tm_h, cookieExpireDays);
        setCookie(formId + "_calcDistTmMinutes", tm_m, cookieExpireDays);
        setCookie(formId + "_calcDistTmSeconds", tm_s, cookieExpireDays);
        setCookie(formId + "_calcDistPaceMinutes", pace_m, cookieExpireDays);
        setCookie(formId + "_calcDistPaceSeconds", pace_s, cookieExpireDays);
        setCookie("calcDistFormLst", String(calcDistFormLst), cookieExpireDays)
    }
    form_ele.querySelector("#distance").value = dist
}

function calcDistance(tm_h, tm_m, tm_s, pace_h, pace_m, pace_s){
    if ((tm_h == '' && tm_m == '' && tm_s == '') && (pace_m == '' && pace_s == '')) {
        return '';
    }

    let tm = time_to_sec(tm_h, tm_m, tm_s);
    let pace = time_to_sec(pace_h, pace_m, pace_s);

    return parseFloat(tm/pace).toFixed(2);
}

/*
Converts passed in hours, minutes, and seconds to seconds an combines them
if h, m, s is an empty string set to 0
*/
function time_to_sec(hour, minute, second){
    if (hour == '') {
        h = 0;
    }else{
        h = parseInt(hour);
    }
    if (minute == '') {
        m = 0;
    }else{
        m = parseInt(minute);
    }
    if (second == '') {
        s = 0;
    }else{
        s = parseInt(second);
    }

    return (h*3600) + (m*60) + (s);
}

/*
Converts passed in seconds to specified time format
*/
function sec_to_time_str(tot_sec, format){
    s = Math.round(tot_sec % 3600 % 60)
    if (format == 'ms'){
        m = Math.floor(tot_sec / 60);
        return m + 'm ' + s + 's'
    }else{
        h = Math.floor(tot_sec / 3600);
        m = Math.floor(tot_sec % 3600 / 60);
        return h + 'h ' + m + 'm ' + s + 's'
    }
}

/*
save cookie for passed in number of days
*/
function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/; Secure";
}

/*
Gets passed in cookie
*/
function getCookie(cname) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

/*
Erase passed in cookie by setting expiration to the past
*/
function eraseCookie(cname){
    // console.log('eraseCookie: ' + cname);
    setCookie(cname,"",-1);
}

/*
Run when the check box for remembering calculations in selected or unselected
*/
function cookieChkChange(){
    var cookieChkStatus = document.getElementById("save_cookie");
    // console.log('cookieChk: ' + cookieChkStatus.checked);

    if (cookieChkStatus.checked == true){
        if (confirm("This will store the values you enter as cookies on your computer. Do you agree to them being stored this way?")){
            saveAllCookieValues();
        }else{
            document.getElementById("save_cookie").checked = false;
        }
    }else{
        eraseAllCookieValues();
    }
}

/*
Run when Remember Calculations check box is selected to save all current calcualtion values as cookies
*/
function saveAllCookieValues(){
    console.log('saveAllCookieValues');
    setCookie("rememberCalculations", true, cookieExpireDays);

    for (i=0; i<calcPaceFormLst.length; i++){
        let formId = calcPaceFormLst[i];
        let calc_pace_form = document.querySelector("#"+formId);
        var h = calc_pace_form.querySelector("#cp_time_h").value;
        var m = calc_pace_form.querySelector("#cp_time_m").value;
        var s = calc_pace_form.querySelector("#cp_time_s").value;
        var dist = calc_pace_form.querySelector("#cp_distance").value;
        setCookie(formId + "_calcPaceHours", h, cookieExpireDays);
        setCookie(formId + "_calcPaceMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcPaceSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcPaceDistance", dist, cookieExpireDays);
    }
    setCookie("calcPaceFormLst", String(calcPaceFormLst), cookieExpireDays)

    for (i=0; i<calcTimeFormLst.length; i++){
        let formId = calcTimeFormLst[i];
        let calc_form = document.querySelector("#"+formId);
        let m = calc_form.querySelector("#ct_pace_m").value;
        let s = calc_form.querySelector("#ct_pace_s").value;
        let dist = calc_form.querySelector("#ct_distance").value;
        setCookie(formId + "_calcTimeMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcTimeSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcTimeDistance", dist, cookieExpireDays);
    }
    setCookie("calcTimeFormLst", String(calcTimeFormLst), cookieExpireDays)

    for (i=0; i<calcAdjPaceFormLst.length; i++){
        let formId = calcAdjPaceFormLst[i];
        let calc_form = document.querySelector("#"+formId);
        let m = calc_form.querySelector("#pace_m").value;
        let s = calc_form.querySelector("#pace_s").value;
        let temperature = calc_form.querySelector("#temperature").value;
        setCookie(formId + "_calcAdjPaceMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcAdjPaceSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcAdjPaceTemperature", temperature, cookieExpireDays);
    }
    setCookie("calcAdjPaceFormLst", String(calcAdjPaceFormLst), cookieExpireDays)

    for (i=0; i<calcDistFormLst.length; i++){
        let formId = calcDistFormLst[i];
        let calc_form = document.querySelector("#"+formId);
        let tm_h = calc_form.querySelector("#time_h").value;
        let tm_m = calc_form.querySelector("#time_m").value;
        let tm_s = calc_form.querySelector("#time_s").value;
        let pace_m = calc_form.querySelector("#pace_m").value;
        let pace_s = calc_form.querySelector("#pace_s").value;
        // let dist = calc_form.querySelector("#ct_distance").value;
        setCookie(formId + "_calcDistTmHours", tm_h, cookieExpireDays);
        setCookie(formId + "_calcDistTmMinutes", tm_m, cookieExpireDays);
        setCookie(formId + "_calcDistTmSeconds", tm_s, cookieExpireDays);
        setCookie(formId + "_calcDistPaceMinutes", pace_m, cookieExpireDays);
        setCookie(formId + "_calcDistPaceSeconds", pace_s, cookieExpireDays);
    }
    setCookie("calcDistFormLst", String(calcDistFormLst), cookieExpireDays)
}

/*
Run when Remember Calculations check box is un-selected to remove all current calcualtion value cookies. Does not affect the values on the web page.
*/
function eraseAllCookieValues(){
    console.log('eraseAllCookieValues');

    //Erase cookies for calculating pace from distance and time
    for (i=0; i<calcPaceFormLst.length; i++){
        let formId = calcPaceFormLst[i];
        eraseCookie(formId + "_calcPaceHours");
        eraseCookie(formId + "_calcPaceMinutes");
        eraseCookie(formId + "_calcPaceSeconds");
        eraseCookie(formId + "_calcPaceDistance");
    }
    eraseCookie("calcPaceFormLst")
    calcPaceFormLst = [];

    for (i=0; i<calcTimeFormLst.length; i++){
        let formId = calcTimeFormLst[i];
        eraseCookie(formId + "_calcTimeMinutes");
        eraseCookie(formId + "_calcTimeSeconds");
        eraseCookie(formId + "_calcTimeDistance");
    }
    eraseCookie("calcTimeFormLst");
    calcTimeFormLst = [];

    for (i=0; i<calcAdjPaceFormLst.length; i++){
        let formId = calcAdjPaceFormLst[i];
        eraseCookie(formId + "_calcAdjPaceMinutes");
        eraseCookie(formId + "_calcAdjPaceSeconds");
        eraseCookie(formId + "_calcPaceSeconds");
        eraseCookie(formId + "_calcAdjPaceTemperature");
    }
    eraseCookie("calcAdjPaceFormLst");
    calcAdjPaceFormLst = [];

    for (i=0; i<calcDistFormLst.length; i++){
        let formId = calcDistFormLst[i];
        eraseCookie(formId + "_calcDistTmHours");
        eraseCookie(formId + "_calcDistTmMinutes");
        eraseCookie(formId + "_calcDistTmSeconds");
        eraseCookie(formId + "_calcDistPaceMinutes");
        eraseCookie(formId + "_calcDistPaceSeconds");
    }
    eraseCookie("calcDistFormLst");
    calcDistFormLst = [];

    //Erase the cookie for remembering calculations
    eraseCookie("rememberCalculations");
}

/*
Run on page loade. Checks if rememberCalculations cookie is set and if it is reads in cookies for each calculation and populates their values on the web page.
*/
function reloadCalculationValues(){
    var rememberCalc = getCookie("rememberCalculations");
    if (rememberCalc){
        document.getElementById("save_cookie").checked = true;

        let calcPaceCt = getCalcPacePrevious();
        if (calcPaceCt <1){
            newCalcPace();
        }
        let calcTimeCt = getCalcTimePrevious();
        if (calcTimeCt <1){
            newCalcTime();
        }

        if (getCalcAdjPacePrevious() <1){
            newCalcAdjPace();
        }

        let calcDistCt = getCalcDistancePrevious();
        if (calcDistCt <1){
            newCalcDist();
        }

        //this is done so when user visits the page the cookies will get saved with new set of days to live
        saveAllCookieValues();
    }else{
        newCalcPace();
        newCalcTime();
        newCalcDist();
        newCalcAdjPace();
    }
}

/*
Get cookie values for Calculating pace, populates the web page fields, and calculates the pace.
Returns number of calculate pace forms generated
*/
function getCalcPacePrevious(){
    let calcPaceCookieLst = getCookie("calcPaceFormLst").split(',');
    console.log('getCalcPacePrevious: ' + String(calcPaceCookieLst));

    for (i=0; i<calcPaceCookieLst.length; i++){
        let formId = calcPaceCookieLst[i];
        newFormId = newCalcPace();
        let calc_pace_form = document.querySelector("#"+newFormId);
        h = getCookie(formId + "_calcPaceHours");
        m = getCookie(formId + "_calcPaceMinutes");
        s = getCookie(formId + "_calcPaceSeconds");
        dist = getCookie(formId + "_calcPaceDistance");

        eraseCookie(formId + "_calcPaceHours");
        eraseCookie(formId + "_calcPaceMinutes");
        eraseCookie(formId + "_calcPaceSeconds");
        eraseCookie(formId + "_calcPaceDistance");

        calc_pace_form.querySelector("#cp_time_h").value = h;
        calc_pace_form.querySelector("#cp_time_m").value = m;
        calc_pace_form.querySelector("#cp_time_s").value = s;
        calc_pace_form.querySelector("#cp_distance").value = dist;

        if (dist != ''){
            calc_pace_form.querySelector("#cp_pace").value = sec_to_time_str(calcPace(h,m,s,dist));
        }
        calcPaceFormLst.push(newFormId);

    }
    return calcPaceCookieLst.length;
}

/*
Get cookie values for Calculating time, populates the web page fields, and calculates the time.
*/
function getCalcTimePrevious(){
    let calcTimeCookieLst = getCookie("calcTimeFormLst").split(',');
    console.log('getCalcTimePrevious: ' + String(calcTimeCookieLst));

    for (i=0; i<calcTimeCookieLst.length; i++){
        let formId = calcTimeCookieLst[i];
        newFormId = newCalcTime();
        let calc_form = document.querySelector("#"+newFormId);

        let m = getCookie(formId + "_calcTimeMinutes");
        let s = getCookie(formId + "_calcTimeSeconds");
        let dist = getCookie(formId + "_calcTimeDistance");

        eraseCookie(formId + "_calcTimeMinutes");
        eraseCookie(formId + "_calcTimeSeconds");
        eraseCookie(formId + "_calcTimeDistance");

        calc_form.querySelector("#ct_pace_m").value = m;
        calc_form.querySelector("#ct_pace_s").value = s;
        calc_form.querySelector("#ct_distance").value = dist;

        if (dist != ''){
            calc_form.querySelector("#ct_time").value = sec_to_time_str(calcTime(0,m,s,dist));
        }
        calcTimeFormLst.push(newFormId);

    }
    return calcTimeFormLst.length;
}

/*
Get cookie values for Calculating adjusted pace, populates the web page fields, and calculates the adjusted pace.
*/
function getCalcAdjPacePrevious(){
    let calcAdjPaceCookieLst = getCookie("calcAdjPaceFormLst").split(',');
    console.log('getCalcTimePrevious: ' + String(calcAdjPaceCookieLst));

    for (i=0; i<calcAdjPaceCookieLst.length; i++){
        let formId = calcAdjPaceCookieLst[i];
        newFormId = newCalcAdjPace();
        let calc_form = document.querySelector("#"+newFormId);

        let m = getCookie(formId + "_calcAdjPaceMinutes");
        let s = getCookie(formId + "_calcAdjPaceSeconds");
        let temperature = getCookie(formId + "_calcAdjPaceTemperature");

        eraseCookie(formId + "_calcAdjPaceMinutes");
        eraseCookie(formId + "_calcAdjPaceSeconds");
        eraseCookie(formId + "_calcAdjPaceTemperature");

        calc_form.querySelector("#pace_m").value = m;
        calc_form.querySelector("#pace_s").value = s;
        calc_form.querySelector("#temperature").value = temperature;

        if (temperature != ''){
            calc_form.querySelector("#adjusted_pace").value = sec_to_time_str(calcAdjPace(0, m, s, temperature), 'ms');
        }
        calcAdjPaceFormLst.push(newFormId);

    }
    return calcAdjPaceFormLst.length;
}

/*
Get cookie values for Calculating distance, populates the web page fields, and calculates the pace.
*/
function getCalcDistancePrevious(){
    let calcCookieLst = getCookie("calcDistFormLst").split(',');
    console.log('getCalcDistPrevious: ' + String(calcCookieLst));

    for (i=0; i<calcCookieLst.length; i++){
        let formId = calcCookieLst[i];
        newFormId = newCalcDist();
        let calc_form = document.querySelector("#"+newFormId);

        let tm_h = getCookie(formId + "_calcDistTmHours");
        let tm_m = getCookie(formId + "_calcDistTmMinutes");
        let tm_s = getCookie(formId + "_calcDistTmSeconds");
        let pace_m = getCookie(formId + "_calcDistPaceMinutes");
        let pace_s = getCookie(formId + "_calcDistPaceSeconds");

        eraseCookie(formId + "_calcDistTmHours");
        eraseCookie(formId + "_calcDistTmMinutes");
        eraseCookie(formId + "_calcDistTmSeconds");
        eraseCookie(formId + "_calcDistPaceMinutes");
        eraseCookie(formId + "_calcDistPaceSeconds");

        calc_form.querySelector("#time_h").value = tm_h;
        calc_form.querySelector("#time_m").value = tm_m;
        calc_form.querySelector("#time_s").value = tm_s;
        calc_form.querySelector("#pace_m").value = pace_m;
        calc_form.querySelector("#pace_s").value = pace_s;

        calc_form.querySelector("#distance").value = calcDistance(tm_h, tm_m, tm_s, 0, pace_m, pace_s);

        calcDistFormLst.push(newFormId);

    }
    return calcDistFormLst.length;
}

/*
Used for create new calculation row from button, only calls the function to create the new row. This is needed since cannot have the function return a value when called by an HTML button.
*/
function newCalcPaceBtn(){
    newCalcPace();
}
function newCalcTimeBtn(){
    newCalcTime();
}
function newCalcDistBtn(){
    newCalcDist();
}
function newCalcAdjPaceBtn(){
    newCalcAdjPace();
}

/*
Create new calculation row
Return ID of form for row that was created
*/
function newCalcPace(){
    paceFormCt++;
    newFormId = 'pace_from_dist_time_'+paceFormCt;

    let calc_pace_lst = document.getElementById('calc_pace_from_dist_tm_lst');
    let template_calc_pace = document.getElementById("calc_pace_from_dist_tm").content.cloneNode(true);
    formTag = template_calc_pace.querySelector("form");
    formTag.id = newFormId;
    formTag.action = "JavaScript:calcPaceBtn('"+newFormId+"')";
    rmBtnTag = template_calc_pace.querySelector("#cp_rm_btn");
    rmBtnTag.setAttribute("onclick", "JavaScript:removeCalcPaceRow('"+newFormId+"');");

    calc_pace_lst.appendChild(template_calc_pace);
    return newFormId;

}

/*
Create new calculation row
Return ID of form for row that was created
*/
function newCalcTime(){
    timeFormCt++;
    newFormId = 'time_from_dist_pace_'+timeFormCt;

    let calc_lst = document.getElementById('calc_time_from_dist_pace_lst');
    let template_calc = document.getElementById("calc_time_from_dist_pace").content.cloneNode(true);
    formTag = template_calc.querySelector("form");
    formTag.id = newFormId;
    formTag.action = "JavaScript:calcTimeBtn('"+newFormId+"')";
    rmBtnTag = template_calc.querySelector("#calc_rm_btn");
    rmBtnTag.setAttribute("onclick", "JavaScript:removeCalcTimeRow('"+newFormId+"');");

    calc_lst.appendChild(template_calc);
    return newFormId;

}

/*
Create new calculation row
Return ID of form for row that was created
*/
function newCalcDist(){
    distFormCt++;
    newFormId = 'dist_from_time_pace'+distFormCt;

    let calc_lst = document.getElementById('calc_dist_from_time_pace_lst');
    let template_calc = document.getElementById("calc_dist_from_time_pace").content.cloneNode(true);
    formTag = template_calc.querySelector("form");
    formTag.id = newFormId;
    formTag.action = "JavaScript:calcDistBtn('"+newFormId+"')";
    rmBtnTag = template_calc.querySelector("#calc_rm_btn");
    rmBtnTag.setAttribute("onclick", "JavaScript:removeCalcDistRow('"+newFormId+"');");

    calc_lst.appendChild(template_calc);
    return newFormId;

}
/*
Create new calculation row
Return ID of form for row that was created
*/
function newCalcAdjPace(){
    adjPaceFormCt++;
    newFormId = 'adjpace_from_temperature_pace'+adjPaceFormCt;

    let calc_lst = document.getElementById('calc_adjpace_from_temp_pace_lst');
    let template_calc = document.getElementById("calc_adjpace_from_temp_pace").content.cloneNode(true);
    formTag = template_calc.querySelector("form");
    formTag.id = newFormId;
    formTag.action = "JavaScript:calcAdjPaceBtn('"+newFormId+"')";
    rmBtnTag = template_calc.querySelector("#calc_rm_btn");
    rmBtnTag.setAttribute("onclick", "JavaScript:removeCalcAdjPaceRow('"+newFormId+"');");

    calc_lst.appendChild(template_calc);
    return newFormId;

}

/*
Remove row for rowId of Calculate Pace from Distance and Time
Then remove cookies for the row
*/
function removeCalcPaceRow(rowId){
    console.log("removeCalcPaceRow: " + rowId);
    let divToRemove = document.getElementById(rowId).parentElement;

    let calc_pace_lst = document.getElementById('calc_pace_from_dist_tm_lst');
    calc_pace_lst.removeChild(divToRemove);

    //Remove cookies
    eraseCookie(rowId + "_calcPaceHours");
    eraseCookie(rowId + "_calcPaceMinutes");
    eraseCookie(rowId + "_calcPaceSeconds");
    eraseCookie(rowId + "_calcPaceDistance");
    let index = calcPaceFormLst.indexOf(rowId);
    if (index != -1) {
        calcPaceFormLst.splice(index, 1);
    }
    setCookie("calcPaceFormLst", String(calcPaceFormLst), cookieExpireDays);

    //If there are no more rows then add a new blank one
    let calc_ct = calc_pace_lst.querySelectorAll(".calc_row").length;
    if (calc_ct <=0){
        newCalcPace();
    }
}
/*
Remove row for rowId of Calculate Time from Distance and Pace
Then remove cookies for the row
*/
function removeCalcTimeRow(rowId){
    console.log("removeCalcTimeRow: " + rowId);
    let divToRemove = document.getElementById(rowId).parentElement;

    let calc_lst = document.getElementById('calc_time_from_dist_pace_lst');
    calc_lst.removeChild(divToRemove);

    //Remove cookies
    eraseCookie(rowId + "_calcTimeMinutes");
    eraseCookie(rowId + "_calcTimeSeconds");
    eraseCookie(rowId + "_calcTimeDistance");
    let index = calcTimeFormLst.indexOf(rowId);
    if (index != -1) {
        calcTimeFormLst.splice(index, 1);
    }
    setCookie("calcTimeFormLst", String(calcTimeFormLst), cookieExpireDays);

    //If there are no more rows then add a new blank one
    let calc_ct = calc_lst.querySelectorAll(".calc_row").length;
    if (calc_ct <=0){
        newCalcTime();
    }
}
/*
Remove row for rowId of Calculate Distance from Time and Pace
Then remove cookies for the row
*/
function removeCalcDistRow(rowId){
    console.log("removeCalcDistRow: " + rowId);
    let divToRemove = document.getElementById(rowId).parentElement;

    let calc_lst = document.getElementById('calc_dist_from_time_pace_lst');
    calc_lst.removeChild(divToRemove);

    //Remove cookies
    eraseCookie(rowId + "_calcDistTmHours");
    eraseCookie(rowId + "_calcDistTmMinutes");
    eraseCookie(rowId + "_calcDistTmSeconds");
    eraseCookie(rowId + "_calcDistTmHours");
    eraseCookie(rowId + "_calcDistPaceMinutes");
    eraseCookie(rowId + "_calcDistPaceSeconds");

    let index = calcDistFormLst.indexOf(rowId);
    if (index != -1) {
        calcDistFormLst.splice(index, 1);
    }
    setCookie("calcDistFormLst", String(calcDistFormLst), cookieExpireDays);

    //If there are no more rows then add a new blank one
    let calc_ct = calc_lst.querySelectorAll(".calc_row").length;
    if (calc_ct <=0){
        newCalcDist();
    }
}
/*
Remove row for rowId of Calculate Adjusted Pace from Temperature and desired Pace
Then remove cookies for the row
*/
function removeCalcAdjPaceRow(rowId){
    console.log("removeCalcAdjPaceRow: " + rowId);
    let divToRemove = document.getElementById(rowId).parentElement;

    let calc_lst = document.getElementById('calc_adjpace_from_temp_pace_lst');
    calc_lst.removeChild(divToRemove);

    //Remove cookies
    eraseCookie(rowId + "_calcAdjPaceMinutes");
    eraseCookie(rowId + "_calcAdjPaceSeconds");
    eraseCookie(rowId + "_calcAdjPaceTemperature");

    let index = calcAdjPaceFormLst.indexOf(rowId);
    if (index != -1) {
        calcAdjPaceFormLst.splice(index, 1);
    }
    setCookie("calcAdjPaceFormLst", String(calcAdjPaceFormLst), cookieExpireDays);

    //If there are no more rows then add a new blank one
    let calc_ct = calc_lst.querySelectorAll(".calc_row").length;
    if (calc_ct <=0){
        newCalcAdjPace();
    }
}

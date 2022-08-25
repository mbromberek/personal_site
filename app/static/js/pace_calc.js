//List of cookies being saved for different values
var calculationCookieLst = [
    'calcPaceHours','calcPaceMinutes','calcPaceSeconds','calcPaceDistance',
    'calcTimeMinutes', 'calcTimeSeconds', 'calcTimeDistance',
    'calcPaceAdjMinutes', 'calcPaceAdjSeconds', 'calcPaceAdjTemperature',
    'calcDistTmHours', 'calcDistTmMinutes', 'calcDistTmSeconds', 'calcDistPaceMinutes', 'calcDistPaceSeconds'
];
var calcPaceFormLst = [];


//Number of days to save cookies for
var cookieExpireDays = 60;
var paceFormCt = 0;

/*
Run when calculate button is pressed for getting pace
Saves fields as cookies if they are populated and Remember Calculations is checked
*/
function calcPaceBtn(formId){
    console.log(formId);
    let form_ele = document.getElementById(formId);

    let h = form_ele.querySelector("#cp_time_h").value;
    let m = form_ele.querySelector("#cp_time_m").value;
    let s = form_ele.querySelector("#cp_time_s").value;
    let dist = form_ele.querySelector("#cp_distance").value;
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie(formId + "_calcPaceHours", h, cookieExpireDays);
        setCookie(formId + "_calcPaceMinutes", m, cookieExpireDays);
        setCookie(formId + "_calcPaceSeconds", s, cookieExpireDays);
        setCookie(formId + "_calcPaceDistance", dist, cookieExpireDays);
        setCookie("calcPaceFromDistTm", String(calcPaceFormLst), cookieExpireDays)
    }
    if (!(calcPaceFormLst.includes(formId))) {
        calcPaceFormLst.push(formId);
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
function calcTimeBtn(){
    var dist = document.getElementById("ct_distance").value;
    var m = document.getElementById("ct_pace_m").value;
    var s = document.getElementById("ct_pace_s").value;
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie("calcTimeMinutes", m, cookieExpireDays);
        setCookie("calcTimeSeconds", s, cookieExpireDays);
        setCookie("calcTimeDistance", dist, cookieExpireDays);
    }

    document.getElementById("ct_time").value = sec_to_time_str(calcTime(0,m,s,dist));
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
function calcPaceHeatBtn(){
    var m = document.getElementById("cpt_desired_pace_m").value;
    var s = document.getElementById("cpt_desired_pace_s").value;
    var temp = document.getElementById("cpt_temperature").value;
    if (temp != '' && document.getElementById("save_cookie").checked){
        setCookie("calcPaceAdjMinutes", m, cookieExpireDays);
        setCookie("calcPaceAdjSeconds", s, cookieExpireDays);
        setCookie("calcPaceAdjTemperature", temp, cookieExpireDays);
    }

    document.getElementById("cpt_adjusted_pace").value = sec_to_time_str(calcPaceHeat(0, m, s, temp), 'ms');
}

function calcPaceHeat(h, m, s, temp){
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
function calcDistanceBtn(formId){
    form_ele = document.getElementById(formId);
    let tm_h = form_ele.querySelector("#cd_time_h").value;
    let tm_m = form_ele.querySelector("#cd_time_m").value;
    let tm_s = form_ele.querySelector("#cd_time_s").value;
    let pace_m = form_ele.querySelector("#cd_pace_m").value;
    let pace_s = form_ele.querySelector("#cd_pace_s").value;
    let dist = '';

    //Need at least one value for time or pace
    if ((tm_h != '' || tm_m != '' || tm_s != '') || (pace_m != '' || pace_s != '')) {
        dist = calcDistance(tm_h, tm_m, tm_s, 0, pace_m, pace_s);
    }else{
        alert('Please enter a value for Time and Pace')
    }
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie(formId + "_calcDistTmHours", tm_h, cookieExpireDays);
        setCookie(formId + "_calcDistTmMinutes", tm_m, cookieExpireDays);
        setCookie(formId + "_calcDistTmSeconds", tm_s, cookieExpireDays);
        setCookie(formId + "_calcDistPaceMinutes", pace_m, cookieExpireDays);
        setCookie(formId + "_calcDistPaceSeconds", pace_s, cookieExpireDays);
    }
    form_ele.querySelector("#cd_distance").value = dist
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
    console.log('cookieChk: ' + cookieChkStatus.checked);

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

    setCookie("dist_form_ids", 'dist_from_time_pace_1,dist_from_time_pace_2', cookieExpireDays);

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
        console.log('saved cookies for form: ' + formId);
    }
    setCookie("calcPaceFromDistTm", String(calcPaceFormLst), cookieExpireDays)

    var dist = document.getElementById("ct_distance").value;
    var m = document.getElementById("ct_pace_m").value;
    var s = document.getElementById("ct_pace_s").value;
    setCookie("calcTimeMinutes", m, cookieExpireDays);
    setCookie("calcTimeSeconds", s, cookieExpireDays);
    setCookie("calcTimeDistance", dist, cookieExpireDays);

    var m = document.getElementById("cpt_desired_pace_m").value;
    var s = document.getElementById("cpt_desired_pace_s").value;
    var temp = document.getElementById("cpt_temperature").value;
    setCookie("calcPaceAdjMinutes", m, cookieExpireDays);
    setCookie("calcPaceAdjSeconds", s, cookieExpireDays);
    setCookie("calcPaceAdjTemperature", temp, cookieExpireDays);

    formId = 'dist_from_time_pace_1';
    form_ele = document.getElementById(formId);
    let tm_h = form_ele.querySelector("#cd_time_h").value;
    let tm_m = form_ele.querySelector("#cd_time_m").value;
    let tm_s = form_ele.querySelector("#cd_time_s").value;
    let pace_m = form_ele.querySelector("#cd_pace_m").value;
    let pace_s = form_ele.querySelector("#cd_pace_s").value;
    setCookie(formId + "_calcDistTmHours", tm_h, cookieExpireDays);
    setCookie(formId + "_calcDistTmMinutes", tm_m, cookieExpireDays);
    setCookie(formId + "_calcDistTmSeconds", tm_s, cookieExpireDays);
    setCookie(formId + "_calcDistPaceMinutes", pace_m, cookieExpireDays);
    setCookie(formId + "_calcDistPaceSeconds", pace_s, cookieExpireDays);

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
    eraseCookie("calcPaceFromDistTm")

    //Erase other cookies
    for (var i=0; i<calculationCookieLst.length; i++){
        eraseCookie(calculationCookieLst[i]);
    }

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
        getCalcTimePrevious();
        getCalcAdjPacePrevious();

        form_ids = getCookie("dist_form_ids").split(',');
        // console.log(form_ids);
        for (let i=0; i<form_ids.length; i++){
            getCalcDistancePrevious(form_ids[i]);
        }
        //this is done so when user visits the page the cookies will get saved with new set of days to live
        saveAllCookieValues();
    }else{
        newCalcPace();
    }
}

/*
Get cookie values for Calculating pace, populates the web page fields, and calculates the pace.
Returns number of calculate pace forms generated
*/
function getCalcPacePrevious(){
    let calcPaceCookieLst = getCookie("calcPaceFromDistTm").split(',');
    console.log('getCalcPacePrevious: ' + String(calcPaceCookieLst));

    for (i=0; i<calcPaceCookieLst.length; i++){
        let formId = calcPaceCookieLst[i];
        newFormId = newCalcPace();
        let calc_pace_form = document.querySelector("#"+newFormId);
        h = getCookie(formId + "_calcPaceHours");
        m = getCookie(formId + "_calcPaceMinutes");
        s = getCookie(formId + "_calcPaceSeconds");
        dist = getCookie(formId + "_calcPaceDistance");

        //TODO Save cookies to remove to a list and remove just before saving new forms
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
    var m = getCookie("calcTimeMinutes");
    var s = getCookie("calcTimeSeconds");
    var dist = getCookie("calcTimeDistance");

    document.getElementById("ct_pace_m").value = m;
    document.getElementById("ct_pace_s").value = s;
    document.getElementById("ct_distance").value = dist;

    if (dist != ''){
        document.getElementById("ct_time").value = sec_to_time_str(calcTime(0,m,s,dist));
    }
}

/*
Get cookie values for Calculating adjusted pace, populates the web page fields, and calculates the adjusted pace.
*/
function getCalcAdjPacePrevious(){
    var m = getCookie("calcPaceAdjMinutes");
    var s = getCookie("calcPaceAdjSeconds");
    var temp = getCookie("calcPaceAdjTemperature");

    document.getElementById("cpt_desired_pace_m").value = m;
    document.getElementById("cpt_desired_pace_s").value = s;
    document.getElementById("cpt_temperature").value = temp;

    if (temp != ''){
        document.getElementById("cpt_adjusted_pace").value = sec_to_time_str(calcPaceHeat(0, m, s, temp), 'ms');
    }
}

/*
Get cookie values for Calculating distance, populates the web page fields, and calculates the pace.
*/
function getCalcDistancePrevious(formId){
    form_ele = document.getElementById(formId);

    tm_h = getCookie(formId + "_calcDistTmHours");
    tm_m = getCookie(formId + "_calcDistTmMinutes");
    tm_s = getCookie(formId + "_calcDistTmSeconds");
    pace_m = getCookie(formId + "_calcDistPaceMinutes");
    pace_s = getCookie(formId + "_calcDistPaceSeconds");

    form_ele.querySelector("#cd_time_h").value = tm_h;
    form_ele.querySelector("#cd_time_m").value = tm_m;
    form_ele.querySelector("#cd_time_s").value = tm_s;
    form_ele.querySelector("#cd_pace_m").value = pace_m;
    form_ele.querySelector("#cd_pace_s").value = pace_s;

    form_ele.querySelector("#cd_distance").value = calcDistance(tm_h, tm_m, tm_s, 0, pace_m, pace_s);

}

function newCalcPaceBtn(){
    newCalcPace()
}
function newCalcPace(){
    paceFormCt++;
    newFormId = 'pace_from_dist_time_'+paceFormCt;

    let calc_pace_lst = document.getElementById('calc_pace_from_dist_tm_lst');
    let template_calc_pace = document.getElementById("calc_pace_from_dist_tm").content.cloneNode(true);
    formTag = template_calc_pace.querySelector("form");
    formTag.id = newFormId;
    formTag.action = "JavaScript:calcPaceBtn('"+newFormId+"')";
    calc_pace_lst.appendChild(template_calc_pace);
    return newFormId;

}

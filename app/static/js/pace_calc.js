let calculationCookieLst = [
    'calcPaceHours','calcPaceMinutes','calcPaceSeconds','calcPaceDistance',
    'calcTimeMinutes', 'calcTimeSeconds', 'calcTimeDistance',
    'calcPaceAdjMinutes', 'calcPaceAdjSeconds', 'calcPaceAdjTemperature'
];

let cookieExpireDays = 7;

/*
Calculate Pace using the distance and time
Converts hours, minutes, seconds to seconds and sums together
Pace = Time in Seconds / Distance
*/
function calcPace(){
    var h = document.getElementById("cp_time_h").value;
    var m = document.getElementById("cp_time_m").value;
    var s = document.getElementById("cp_time_s").value;
    var dist = document.getElementById("cp_distance").value;
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie("calcPaceHours", h, cookieExpireDays);
        setCookie("calcPaceMinutes", m, cookieExpireDays);
        setCookie("calcPaceSeconds", s, cookieExpireDays);
        setCookie("calcPaceDistance", dist, cookieExpireDays);
    }

    var time_sec = time_to_sec(h, m, s)
    console.log('Entered time seconds: ' + time_sec);

    var pace_sec = Math.round(time_sec / dist);
    console.log('Calculated pace seconds: ' + pace_sec)
    var pace_str = sec_to_time_str(pace_sec, 'ms')
    document.getElementById("cp_pace").value = pace_str;
}

/*
Calculate Time using the distance and pace
Converts the pace minutes and seconds to seconds and sums together
Time = Pace in Seconds * Distance
*/
function calcTime(){
    var dist = document.getElementById("ct_distance").value;
    var m = document.getElementById("ct_pace_m").value;
    var s = document.getElementById("ct_pace_s").value;
    if (dist != '' && document.getElementById("save_cookie").checked){
        setCookie("calcTimeMinutes", m, cookieExpireDays);
        setCookie("calcTimeSeconds", s, cookieExpireDays);
        setCookie("calcTimeDistance", dist, cookieExpireDays);
    }

    var pace_sec = time_to_sec(0, m, s)
    // console.log('Entered pace seconds: ' + pace_sec);

    var time_sec = pace_sec * dist;
    // console.log('Calculated time seconds: ' + time_sec)
    var time_str = sec_to_time_str(time_sec, 'hms')
    document.getElementById("ct_time").value = time_str;
}

/*
Calculate Adjusted Pace based on temperature and desired pace
Converts the pace minutes and seconds to seconds and sums together
Adjusted Pace = Pace in Seconds + ((temperature - 59) / 1.8) * 4.5)
*/
function calcPaceHeat(){
    var m = document.getElementById("cpt_desired_pace_m").value;
    var s = document.getElementById("cpt_desired_pace_s").value;
    var temp = document.getElementById("cpt_temperature").value;
    if (temp != '' && document.getElementById("save_cookie").checked){
        setCookie("calcPaceAdjMinutes", m, cookieExpireDays);
        setCookie("calcPaceAdjSeconds", s, cookieExpireDays);
        setCookie("calcPaceAdjTemperature", temp, cookieExpireDays);
    }

    //calculate pace normal way
    pace_sec = time_to_sec(0, m, s);

    //if temp is <= 59 degrees fahrenheit then return pace with no adjustment
    if (temp <= 59){
        document.getElementById("cpt_adjusted_pace").value = sec_to_time_str(pace_sec, 'ms');
    }else{
        //increase_per_mile_seconds = ( (temperature - 59) / 1.8) * 4.5
        increase_per_mile_seconds = ( (temp - 59) / 1.8) * 4.5
        console.log('increase per mile seconds: ' + increase_per_mile_seconds)
        document.getElementById("cpt_adjusted_pace").value = sec_to_time_str(pace_sec+increase_per_mile_seconds, 'ms');
    }
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


function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/; Secure";
}

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

function cookieChk(){
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

function saveAllCookieValues(){
    console.log('saveAllCookieValues');
    setCookie("rememberCalculations", true, cookieExpireDays);

    var h = document.getElementById("cp_time_h").value;
    var m = document.getElementById("cp_time_m").value;
    var s = document.getElementById("cp_time_s").value;
    var dist = document.getElementById("cp_distance").value;
    setCookie("calcPaceHours", h, cookieExpireDays);
    setCookie("calcPaceMinutes", m, cookieExpireDays);
    setCookie("calcPaceSeconds", s, cookieExpireDays);
    setCookie("calcPaceDistance", dist, cookieExpireDays);

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

}

function eraseAllCookieValues(){
    console.log('eraseAllCookieValues');
    for (var i=0; i<calculationCookieLst.length; i++){
        eraseCookie(calculationCookieLst[i]);
    }
    eraseCookie("rememberCalculations");
}

function eraseCookie(cname){
    console.log('eraseCookie: ' + cname);
    setCookie(cname,"",-1);
}

function reloadCalculationValues(){
    var rememberCalc = getCookie("rememberCalculations");
    if (rememberCalc){
        document.getElementById("save_cookie").checked = true;
        getCalcPacePrevious();
        getCalcTimePrevious();
        getCalcAdjPacePrevious();
    }
}

function getCalcPacePrevious(){
    h = getCookie("calcPaceHours");
    m = getCookie("calcPaceMinutes");
    s = getCookie("calcPaceSeconds");
    dist = getCookie("calcPaceDistance");
    // alert(h + m + s + ", " + dist);

    document.getElementById("cp_time_h").value = h;
    document.getElementById("cp_time_m").value = m;
    document.getElementById("cp_time_s").value = s;
    document.getElementById("cp_distance").value = dist;

    if (dist != ''){
        calcPace();
    }
}

function getCalcTimePrevious(){
    var m = getCookie("calcTimeMinutes");
    var s = getCookie("calcTimeSeconds");
    var dist = getCookie("calcTimeDistance");
    console.log('getCalcTimePrevious: ' + dist);

    document.getElementById("ct_pace_m").value = m;
    document.getElementById("ct_pace_s").value = s;
    document.getElementById("ct_distance").value = dist;

    if (dist != ''){
        calcTime();
    }
}

function getCalcAdjPacePrevious(){
    var m = getCookie("calcPaceAdjMinutes");
    var s = getCookie("calcPaceAdjSeconds");
    var temp = getCookie("calcPaceAdjTemperature");

    document.getElementById("cpt_desired_pace_m").value = m;
    document.getElementById("cpt_desired_pace_s").value = s;
    document.getElementById("cpt_temperature").value = temp;

    if (dist != ''){
        calcPaceHeat();
    }
}

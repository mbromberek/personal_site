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

    //calculate pace normal way
    pace_sec = time_to_sec(0, m, s);

    //if temp is <= 59 degrees fahrenheit then return pace with no adjustment
    if (document.getElementById("cpt_temperature").value <= 59){
        document.getElementById("cpt_adjusted_pace").value = sec_to_time_str(pace_sec, 'ms');
    }else{
        //increase_per_mile_seconds = ( (temperature - 59) / 1.8) * 4.5
        increase_per_mile_seconds = ( (document.getElementById("cpt_temperature").value - 59) / 1.8) * 4.5
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

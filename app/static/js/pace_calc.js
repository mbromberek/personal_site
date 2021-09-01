function calcPace(){
    // alert('calculate pace');
    // alert(document.getElementById("distance").value);
    var dist = document.getElementById("cp_distance").value;
    var time_sec = time_to_sec(document.getElementById("cp_time_h").value, document.getElementById("cp_time_m").value, document.getElementById("cp_time_s").value)
    console.log('Entered time seconds: ' + time_sec);

    var pace_sec = Math.round(time_sec / dist);
    console.log('Calculated pace seconds: ' + pace_sec)
    var pace_str = sec_to_time_str(pace_sec, 'ms')
    document.getElementById("cp_pace").value = pace_str;
}

function time_to_sec(h, m, s){
    return parseInt(h*3600) + parseInt(m*60) + parseInt(s);
}

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

function calcTime(){
    var dist = document.getElementById("ct_distance").value;
    var pace_sec = time_to_sec(0, document.getElementById("ct_pace_m").value, document.getElementById("ct_pace_s").value)
    console.log('Entered pace seconds: ' + pace_sec);

    var time_sec = pace_sec * dist;
    console.log('Calculated time seconds: ' + time_sec)
    var time_str = sec_to_time_str(time_sec, 'hms')
    document.getElementById("ct_time").value = time_str;
}

function calcPaceHeat(){
    //calculate pace normal way
    pace_sec = time_to_sec(0, document.getElementById("cpt_desired_pace_m").value, document.getElementById("cpt_desired_pace_s").value);

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

var curr_sch_id = '-1';
var prog_schedule = '';
var my_schedule_set = new Set();
var using_cookie = false; //Used to track if user has used any cookies or if need to confirm cookie access. 
var prog_key = '';
var sel_day = '';
var sel_panel_type = '';
const time_breaks = ['5:00am','6:00am','7:00am','8:00am','9:00am','10:00am','11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm','6:00pm','7:00pm','8:00pm','9:00pm','10:00pm','11:00pm','12:00am','1:00am','2:00am','3:00am','4:00am'];
const weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const MIN_DESKTOP_WIDTH = 700;
const PANEL_COLOR = {"guest":"darkorange", "staff":"green", "attendee":"darkblue", "convention":"darkred","family":"purple"};
var cookie_expire_days = 1;
const sch_cookie_nm = 'AnimeIowaMySchedule';

/**
Called on page load. 
Saves programming schedule list to global variable prog_schedule
Loads programming schedule for Friday. 
 */
function initialize(response){
  console.log(response);

  //Read MySchedule cookie file. If there is already a cookie then set using_cookie to true
  // my_schedule_set = new Set(["2", "4"]);
  let sch_cookie = getCookie(sch_cookie_nm);
  if (sch_cookie != ""){
    my_schedule_set = new Set(getCookie(sch_cookie_nm).split(","));
    using_cookie = true;
  }
  console.log('my_schedule_set');
  console.log(my_schedule_set);

  prog_schedule = response['prog_schedule'];
  //Populate every element in prog_schedule with if they are part of MySchedule or not
  /*for (let i=0; i<prog_schedule.length; i++){
    if (my_schedule_set.has(prog_schedule[i]['id'])){
      prog_schedule[i]['my_schedule'] = true;
    }else{
      prog_schedule[i]['my_schedule'] = false;
    }
  }*/
  prog_key = response['prog_key'];
  console.log('prog_schedule');
  console.log(prog_schedule);

  updateScheduleForToday();
}

/**
Set the selected panel to be filtered and reloads the schedule. 
If panel_type passed is empty sets to All Panels
 */
function updateScheduleForPanel(panel_type, panel_type_name=''){
  sel_panel_type = panel_type;
  ele = document.getElementById('panel_type_filter');
  if (sel_panel_type == ''){
    ele.innerHTML = 'All Panels';
  }else if(panel_type_name != ''){
    ele.innerHTML = panel_type_name;
  }else{
    ele.innerHTML = sel_panel_type.charAt(0).toUpperCase() 
      + sel_panel_type.slice(1);
  }
  loadSchedule();
}

/**
  Call updateScheduleForDay passing it current day
 */
function updateScheduleForToday(){
  // console.log('updateScheduleForToday');
  const dt = new Date();  
  let decrement_day = 0;
  
  // If current hour is before the first hour of time_breaks then use previous day
  // This is needed since currently setup for a day to start at 5am. 
  //  Do not have to worry about hour being in 24-hour format
  if (dt.getHours() < time_breaks[0].split(':')[0]){
    decrement_day = 1;
  }
  
  updateScheduleForDay(weekday[dt.getDay() -decrement_day]);
}

/**
Set the selected day to be used and reloads the schedule. 
Does nothing if new day is same as selected day
 */
function updateScheduleForDay(day_val){
  // console.log('updateScheduleForDay: ' + day_val);
  if (day_val == sel_day){
    return;
  }
  if (["Friday","Saturday","Sunday"].includes(day_val) ){
    sel_day = day_val;
  }else{
    sel_day = 'Friday';
  }
  ele = document.getElementById('day_filter');
  ele.innerHTML = sel_day;
  loadSchedule();
}

/**
Load schedule based on sel_day and sel_panel_type
If there are no matching entries will have a message saying no panels for selection
 */
function loadSchedule(){
  // console.log('loadSchedule');
  let sch_lst_ele = document.getElementById('sch_lst');

  //Clear out existing schedule from other day
  sch_lst_ele.innerHTML = '';
  curr_sch_id = '-1';
  let firstEle = '-1';
  
  let fillerEle = document.createElement('div');
  fillerEle.setAttribute("id", "nav_space_filler");
  sch_lst_ele.appendChild(fillerEle);
  
  let time_break_pos = 0;
  let newEle = document.createElement('span');
  newEle.setAttribute("id", time_breaks[time_break_pos]);
  sch_lst_ele.insertBefore(newEle, fillerEle);
  
  let itm_load_ct=0;
  let prev_ele = 0;
  //TODO Get Current Day and Current Time to find first element that is close to current day/time to highlight
  for (let i=0; i<prog_schedule.length; i++){
    let panel = prog_schedule[i];
    //TODOMYSCHEDULE: Check if MySchedule filter is selected 
    //Does not use MySchedule filtering
    /*if (panel['day'] != sel_day || 
      (sel_panel_type != '' && panel['panel_type'] != sel_panel_type)
      // || !(my_schedule_set.has(prog_schedule[i]['id'])) 
      ){
      continue;
    }*/
    
    if (panel['day'] != sel_day
      || (sel_panel_type != 'myschedule' && sel_panel_type != '' && panel['panel_type'] != sel_panel_type)
      || (sel_panel_type == 'myschedule' && !my_schedule_set.has(prog_schedule[i]['id'])) 
      ){
      continue;
    }
    
    
    
    // Put time marker above the last entry before the time change so the correct entry is not covered by nav bar
    let panel_start_time_floor = panel['start_time'].replace(':30',':00');
    while (panel_start_time_floor != time_breaks[time_break_pos] && 
        time_break_pos+1<time_breaks.length){
      time_break_pos++;
      let newEle = document.createElement('span');
      newEle.setAttribute("id", time_breaks[time_break_pos]);
      if (itm_load_ct>0){
        let prev_ele = sch_lst_ele.querySelector("#card_"+prev_ele_id);
        sch_lst_ele.insertBefore(newEle, prev_ele);
      }else{
        let prev_ele = sch_lst_ele.querySelector("#nav_space_filler");
        sch_lst_ele.insertBefore(newEle, prev_ele);
      }
    }

    if (panel['title'] == 'CLOSED'){
      continue;
    }
    if (firstEle == '-1'){
      firstEle = i;
    }
        
    let template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
    template_clone.querySelector("#title").innerHTML = panel['title'];
    template_clone.querySelector("#room").innerHTML = panel['room'];
    template_clone.querySelector("#day").innerHTML = panel['day'];
    template_clone.querySelector("#start_time").innerHTML = panel['start_time'];
    
    template_clone.querySelector("#end_time").innerHTML = panel['end_time'];
    
    template_clone.querySelector("#description").innerHTML = panel['description'];
    template_clone.querySelector("#sch_card").setAttribute("onclick", "javascript: showDescription('"+i+"');");
    template_clone.querySelector("#sch_card").classList.add('sch_card_color_'+itm_load_ct%2);
    template_clone.querySelector("#sch_card").classList.add('sch_card_panel_' + panel['panel_type']);
    // template_clone.querySelector("#sch_card").classList.add('sch_card_panel_guest');
    template_clone.querySelector("#sch_card").setAttribute("id", 'card_'+i);
    prev_ele_id = i;
    
    sch_lst_ele.appendChild(template_clone);
    itm_load_ct++;
  }
  while (time_break_pos+1<time_breaks.length){
    time_break_pos++;
    let newEle = document.createElement('span');
    newEle.setAttribute("id", time_breaks[time_break_pos]);
    sch_lst_ele.appendChild(newEle);
  }
  if (itm_load_ct<=0){
    let template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
    template_clone.querySelector("#title").innerHTML = 'No panels matched your filter';
    template_clone.querySelector(".sch_detail").innerHTML = '';
    sch_lst_ele.appendChild(template_clone);
  }

  //Default show panel description on page load for Desktop
  // Checkes firstEle has value
  if (getWidth() >=MIN_DESKTOP_WIDTH && firstEle >=0){
    showDescription(firstEle);
  }

}

/**
show description element for passed in panel id
 */
var showDescription = function(panel_id){
  // console.log(panel_id);
  let panel_ele = document.getElementById('panel_det');
  let sel_sch_det = prog_schedule[panel_id];

  let sch_ele = document.getElementById('card_' + panel_id);
  if (curr_sch_id != '-1'){
    document.getElementById('card_'+curr_sch_id).classList.remove("selected_panel");
    // console.log('Remove:'+prog_schedule[curr_sch_id]['panel_type']);
    // panel_ele.classList.remove("sch_card_panel_"+prog_schedule[curr_sch_id]['panel_type']); //Set panel_det color
  }
  sch_ele.classList.add("selected_panel");
  curr_sch_id = panel_id;

  panel_ele.querySelector("#title").innerHTML = sel_sch_det['title'];
  panel_ele.querySelector("#room").innerHTML = sel_sch_det["room"];
  panel_ele.querySelector("#day").innerHTML = sel_sch_det["day"];
  panel_ele.querySelector("#start_time").innerHTML = sel_sch_det["start_time"];
  panel_ele.querySelector("#end_time").innerHTML = sel_sch_det["end_time"];
  panel_ele.querySelector("#panelists").innerHTML = sel_sch_det["panelists"];
  panel_ele.querySelector("#description").innerHTML = sel_sch_det["description"];
  panel_ele.querySelector("#panel_type").innerHTML = 
    sel_sch_det["panel_type"].charAt(0).toUpperCase() 
    + sel_sch_det["panel_type"].slice(1);
  // console.log(sel_sch_det['panel_type']);
  //panel_ele.classList.add('sch_card_panel_' + sel_sch_det['panel_type']); //Set panel_det color
  panel_ele.style.borderColor = PANEL_COLOR[sel_sch_det['panel_type']];
  panel_ele.style.display = 'inline-block';
  
  panel_ele.querySelector("#myScheduleBtn_mobile").setAttribute("onclick", "javascript: toggleMySchedule('"+sel_sch_det["id"]+"');");
  panel_ele.querySelector("#myScheduleBtn_desktop").setAttribute("onclick", "javascript: toggleMySchedule('"+sel_sch_det["id"]+"');");

  //Set My Schedule button to have plus or check
  if (my_schedule_set.has(sel_sch_det["id"])){
    panel_ele.querySelector("#myScheduleBtnDesktopSymbol").innerHTML = "✔️";
    panel_ele.querySelector("#myScheduleBtnMobileSymbol").innerHTML = "✔️";
  }else{
    panel_ele.querySelector("#myScheduleBtnDesktopSymbol").innerHTML = "➕";
    panel_ele.querySelector("#myScheduleBtnMobileSymbol").innerHTML = "➕";
  }
  
  /**
    Hide schedule list on mobile. 
    Element should already be hidden by description element 
    but this might help with issues from scrolling on mobile

    Removed since it causes the list to go to the top after closing Description
  */
  /*if (getWidth() <MIN_DESKTOP_WIDTH){
    document.getElementById('sch_lst').classList.add('hidden_ele');
  }*/
}

/**
Hide description element and make sure schedule is shown
 */
function closeDescription(){
  console.log("closeDescription");
  document.getElementById("card_"+curr_sch_id).classList.remove("selected_panel");
  // document.getElementById('sch_lst').classList.remove('hidden_ele');
  document.getElementById('panel_det').style.display = 'none';
  curr_sch_id = '-1';
  
}

/**
Add or removes Panel ID to list of panels user has added to their schedule.
- Adds/removes panel ID to a list so can be used in filtering to show My Schedule
- Updates button to show panel is in My Schedule or not
- Adds/removes panel ID from cookie file of My Schedule 
 */
var toggleMySchedule = function(panel_id){
  console.log("toggleMySchedule ID: " + panel_id);

  //Toggle my_schedule flag in prog_schedule for panel
  if (my_schedule_set.has(panel_id)){
    my_schedule_set.delete(panel_id);
  }else{
    
    if (using_cookie == false){
      if (confirm("This will store the values you enter as cookies on your computer. Do you agree to them being stored this way?") == false){
        console.log("Cookie use declined so not using MySchedule");
        return;
      }
    }
    using_cookie = true;
    
    
    my_schedule_set.add(panel_id);
  }

  //TODOMYSCHEDULE: Is this section needed since tracking in my_schedule_set? 
  /*for (let i=0; i<prog_schedule.length; i++){
    if (prog_schedule[i]['id'] == panel_id){
      if (my_schedule_set.has(panel_id)){
        prog_schedule[i]['my_schedule'] = true;
      }else{
        prog_schedule[i]['my_schedule'] = false;
      }
      console.log(prog_schedule[i]);
      break;
    }
  }*/


  //Update buttons to have check mark or Plus on MySchedule buttons
  let panel_ele = document.getElementById('panel_det');  
  if (my_schedule_set.has(panel_id)){
    panel_ele.querySelector("#myScheduleBtnDesktopSymbol").innerHTML = "✔️";
    panel_ele.querySelector("#myScheduleBtnMobileSymbol").innerHTML = "✔️";
  }else{
    panel_ele.querySelector("#myScheduleBtnDesktopSymbol").innerHTML = "➕";
    panel_ele.querySelector("#myScheduleBtnMobileSymbol").innerHTML = "➕";
  }
  
  //TODOMYSCHEDULE: Save new MySchedule item to cookie
  setCookie(sch_cookie_nm, Array.from(my_schedule_set).join(','), cookie_expire_days);
  
  console.log("my_schedule_set");
  console.log(my_schedule_set);
}

/**
Get width of current page, logic came from jQuery
 */
function getWidth() {
  return Math.max(
    document.body.scrollWidth,
    document.documentElement.scrollWidth,
    document.body.offsetWidth,
    document.documentElement.offsetWidth,
    document.documentElement.clientWidth
  );
}

/**
Change to current day and jump to time 
 */
function jumpToCurrTm(){
  // console.log('jumpToCurrTm');

  //UNCOMMENT to jump to current day before current time
  updateScheduleForToday();
  
  const dt = new Date();
  const hr = dt.getHours();
  let tm_period = 'pm';
  if (hr < 12){
    tm_period = 'am';
  }
  let hr_12 = hr%12 || 12;
  let tm_floor_str = hr_12 + ':00' + tm_period;
  
  // console.log(tm_floor_str);
  
  document.getElementById(tm_floor_str).scrollIntoView({behavior: 'smooth'});
  // document.getElementById("7:00pm").scrollIntoView({behavior: 'smooth'});
}

/**
show dropdown menu for passed in navigation item
Closes other menus if open
 */
function showDropdown(nav_nm){
  // console.log("showDropdown");
  if (nav_nm == 'day'){
    document.getElementById('panelDropdown').classList.remove('nav_show');
    document.getElementById('dayDropdown').classList.toggle('nav_show');
  }else if (nav_nm == 'panel'){
    document.getElementById('dayDropdown').classList.remove('nav_show');
    document.getElementById('panelDropdown').classList.toggle('nav_show');
  }else {
    document.getElementById('dayDropdown').classList.remove('nav_show');
    document.getElementById('panelDropdown').classList.remove('nav_show');
  }
}


/**
Close the dropdown menu if the user clicks outside of it
 */
window.onclick = function(event) {
  // console.log('onclick');
  if (!event.target.matches('.dropbtn')) {
    let dropdowns = document.getElementsByClassName("dropdown_content");
    for (let i = 0; i < dropdowns.length; i++) {
      let openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('nav_show')) {
        openDropdown.classList.remove('nav_show');
      }
    }
  }
} 



/*
save cookie for passed in number of days
*/
function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/; SameSite=Strict; Secure;";
  return true;
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


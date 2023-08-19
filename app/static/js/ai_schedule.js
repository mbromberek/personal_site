var curr_sch_id = '';
var prog_schedule = '';
var prog_key = '';
var sel_day = '';
var sel_panel_type = '';
const time_breaks = ['5:00am','6:00am','7:00am','8:00am','9:00am','10:00am','11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm','6:00pm','7:00pm','8:00pm','9:00pm','10:00pm','11:00pm','12:00am','1:00am','2:00am','3:00am','4:00am'];
const weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const MIN_DESKTOP_WIDTH = 700;
const PANEL_COLOR = {"guest":"darkorange", "staff":"green", "attendee":"darkblue", "convention":"darkred","family":"purple"};

/**
Called on page load. 
Saves programming schedule list to global variable prog_schedule
Loads programming schedule for Friday. 
 */
function initialize(response){
  console.log(response);
  prog_schedule = response['prog_schedule'];
  prog_key = response['prog_key'];

  //TODO change to use show current day and default to Friday if not a day with schedules
  updateScheduleForDay('Saturday');
}

function updateScheduleForPanel(panel_type){
  sel_panel_type = panel_type;
  ele = document.getElementById('panel_type_filter');
  if (sel_panel_type == ''){
    ele.innerHTML = 'All Panels';
  }else{
    ele.innerHTML = sel_panel_type.charAt(0).toUpperCase() 
      + sel_panel_type.slice(1);
  }
  loadSchedule();
}

/**
Loads schedule for passed day_val
 */
function updateScheduleForDay(day_val){
  sel_day = day_val;
  ele = document.getElementById('day_filter');
  ele.innerHTML = sel_day;
  loadSchedule();
}

/**
Load schedule based on sel_day and sel_panel_type
 */
function loadSchedule(){
  let sch_lst_ele = document.getElementById('sch_lst');

  //Clear out existing schedule from other day
  sch_lst_ele.innerHTML = '';
  curr_sch_id = '';
  let firstEle = '';
  
  /*document.getElementById('Friday').classList.remove('sch_nav_item_selected');
  document.getElementById('Saturday').classList.remove('sch_nav_item_selected');
  document.getElementById('Sunday').classList.remove('sch_nav_item_selected');
  document.getElementById(sel_day).classList.add('sch_nav_item_selected');*/
  
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
  //TODO Check if there were no items for filter and display a message about that
  for (let i=0; i<prog_schedule.length; i++){
    let panel = prog_schedule[i];
    if (panel['day'] != sel_day || 
      (sel_panel_type != '' && panel['panel_type'] != sel_panel_type)){
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
    if (firstEle == ''){
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
  if (getWidth() >=MIN_DESKTOP_WIDTH){
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
  if (curr_sch_id != ''){
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
  curr_sch_id = '';
  
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
  const dt = new Date();
  
  //UNCOMMENT to jump to current day before current time
  //TODO setup to work when current time is before 4am so want to use previous day
  /*console.log(weekday[dt.getDay()]);
  if (weekday[dt.getDay()] != sel_day){
    loadScheduleForDay(weekday[dt.getDay()]);
  }*/
  const hr = dt.getHours();
  let tm_period = 'pm';
  if (hr < 12){
    tm_period = 'am';
  }
  let hr_12 = hr%12 || 12;
  let tm_floor_str = hr_12 + ':00' + tm_period;
  
  console.log(tm_floor_str);
  
  document.getElementById(tm_floor_str).scrollIntoView({behavior: 'smooth'});
  // document.getElementById("7:00pm").scrollIntoView({behavior: 'smooth'});
}

function showDropdown(nav_nm){
  console.log("showDropdown");
  /*console.log(ele);
  dropDown = document.getElementById(ele);
  if (dropDown.classList.contains('nav_show')) {
    dropDown.classList.remove('nav_show');
  }else{
    dropDown.classList.add('nav_show');
  }*/

  // document.getElementById(ele).classList.toggle("nav_show");
  // document.getElementById(ele).classList.add("nav_show");
  
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


// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  console.log('onclick');
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


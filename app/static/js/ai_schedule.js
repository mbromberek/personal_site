var curr_sch_id = '';
var prog_schedule = '';
var time_breaks = ['5:00am','6:00am','7:00am','8:00am','9:00am','10:00am','11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm','6:00pm','7:00pm','8:00pm','9:00pm','10:00pm','11:00pm','12:00am','1:00am','2:00am','3:00am','4:00am'];


function loadSchedule(response){
  console.log(response);
  
  prog_schedule = response['prog_schedule'];
  let sch_lst_ele = document.getElementById('sch_lst');
  
  let time_break_pos = 0;
  let newEle = document.createElement('span');
  newEle.setAttribute("id", time_breaks[time_break_pos]);
  sch_lst_ele.appendChild(newEle);
  
  let j=0;
  let prev_ele = 0;
  //Get Current Day and Current Time to find first element that is close to current day/time to highlight
  
  for (let i=0; i<prog_schedule.length; i++){
    let panel = prog_schedule[i];
    // Put time marker above the last entry before the time change so the correct entry is not covered by nav bar
    
    let panel_start_time_floor = panel['start_time'].replace(':30',':00');
    while (panel_start_time_floor != time_breaks[time_break_pos] && 
        time_break_pos+1<time_breaks.length){
      /*console.log('panel time actual: ' + panel['start_time']);
      console.log('panel time round: ' + panel_start_time_floor);
      console.log('time_break: ' + time_breaks[time_break_pos]);*/
      time_break_pos++;
      let newEle = document.createElement('span');
      newEle.setAttribute("id", time_breaks[time_break_pos]);
      if (j>0){
        console.log("insertBefore:"+"#card_"+prev_ele_id);
        let prev_ele = sch_lst_ele.querySelector("#card_"+prev_ele_id);
        sch_lst_ele.insertBefore(newEle, prev_ele);
      }else{
        console.log("append:"+j);
        sch_lst_ele.appendChild(newEle);
      }
    }

    if (panel['title'] == 'CLOSED'){
      continue;
    }
        
    let template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
    template_clone.querySelector("#title").innerHTML = panel['title'];
    template_clone.querySelector("#room").innerHTML = panel['room'];
    template_clone.querySelector("#day").innerHTML = panel['day'];
    template_clone.querySelector("#start_time").innerHTML = panel['start_time'];
    
    template_clone.querySelector("#end_time").innerHTML = panel['end_time'];
    
    template_clone.querySelector("#description").innerHTML = panel['description'];
    template_clone.querySelector("#sch_card").setAttribute("onclick", "javascript: showDescription('"+i+"');");
    template_clone.querySelector("#sch_card").classList.add('sch_card_color_'+j%2);
    template_clone.querySelector("#sch_card").classList.add('sch_card_panel_' + panel['panel_type']);
    // template_clone.querySelector("#sch_card").classList.add('sch_card_panel_guest');
    template_clone.querySelector("#sch_card").setAttribute("id", 'card_'+i);
    prev_ele_id = i;
    
    sch_lst_ele.appendChild(template_clone);
    j++;
  }
  while (time_break_pos+1<time_breaks.length){
    time_break_pos++;
    let newEle = document.createElement('span');
    newEle.setAttribute("id", time_breaks[time_break_pos]);
    sch_lst_ele.appendChild(newEle);
  }

  //Default show panel description on page load for Desktop
  if (getWidth() >=600){
    showDescription("0");
  }

}

var showDescription = function(panel_id){
  // console.log(panel_id);
  let panel_ele = document.getElementById('panel_det');
  let sel_sch_det = prog_schedule[panel_id];

  let sch_ele = document.getElementById('card_' + panel_id);
  sch_ele.classList.add("selected_panel");
  if (curr_sch_id != ''){
    document.getElementById('card_'+curr_sch_id).classList.remove("selected_panel");
    // console.log('Remove:'+prog_schedule[curr_sch_id]['panel_type']);
    panel_ele.classList.remove("sch_card_panel_"+prog_schedule[curr_sch_id]['panel_type']);
  }
  curr_sch_id = panel_id;

  panel_ele.querySelector("#title").innerHTML = sel_sch_det['title'];
  panel_ele.querySelector("#room").innerHTML = sel_sch_det["room"];
  panel_ele.querySelector("#day").innerHTML = sel_sch_det["day"];
  panel_ele.querySelector("#start_time").innerHTML = sel_sch_det["start_time"];
  panel_ele.querySelector("#end_time").innerHTML = sel_sch_det["end_time"];
  panel_ele.querySelector("#panelists").innerHTML = sel_sch_det["panelists"];
  panel_ele.querySelector("#description").innerHTML = sel_sch_det["description"];
  // console.log(sel_sch_det['panel_type']);
  panel_ele.classList.add('sch_card_panel_' + sel_sch_det['panel_type']);
  panel_ele.style.display = 'inline-block';
  
  
}

function closeDescription(){
  console.log("closeDescription");
  document.getElementById("card_"+curr_sch_id).classList.remove("selected_panel");
  document.getElementById('panel_det').style.display = 'none';
  curr_sch_id = '';
  
}

function getWidth() {
  return Math.max(
    document.body.scrollWidth,
    document.documentElement.scrollWidth,
    document.body.offsetWidth,
    document.documentElement.offsetWidth,
    document.documentElement.clientWidth
  );
}

function jumpToCurrTm(){
  const date = new Date();
  const hr = date.getHours();
  let tm_period = 'pm';
  if (hr < 12){
    tm_period = 'am';
  }
  let hr_12 = hr%12 || 12;
  let tm_floor_str = hr_12 + ':00' + tm_period;
  
  console.log(tm_floor_str);
  
  // document.getElementById(tm_floor_str).scrollIntoView({behavior: 'smooth'});
  document.getElementById("7:00pm").scrollIntoView({behavior: 'smooth'});
}
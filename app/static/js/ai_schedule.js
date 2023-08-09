var curr_sch_id = '';

function loadSchedule(response){
  console.log(response);
  
  let prog_schedule = response['prog_schedule'];
  let sch_lst_ele = document.getElementById('sch_lst');
  let j=0;
  //Get Current Day and Current Time to find first element that is close to current day/time to highlight
  
  for (let i=0; i<prog_schedule.length; i++){
    let panel = prog_schedule[i];
    if (panel['title'] == 'CLOSED'){
      continue;
    }
    let template_clone = document.getElementsByTagName("template")[0].content.cloneNode(true);
    template_clone.querySelector("#title").innerHTML = panel['title'];
    template_clone.querySelector("#room").innerHTML = panel['room'];
    template_clone.querySelector("#day").innerHTML = panel['day'];
    template_clone.querySelector("#start_time").innerHTML = panel['start_time'];
    template_clone.querySelector("#end_time").innerHTML = panel['end_time'];
    template_clone.querySelector("#panelists").innerHTML = panel['panelists'];
    
    template_clone.querySelector("#description").innerHTML = panel['description'];
    template_clone.querySelector("#sch_card").setAttribute("onclick", "javascript: showDescription('card_"+j+"');");
    template_clone.querySelector("#sch_card").classList.add('sch_card_color_'+j%2);
    template_clone.querySelector("#sch_card").setAttribute("id", 'card_'+j);
    
    sch_lst_ele.appendChild(template_clone);
    j++;
  }
  showDescription("card_0");

}

var showDescription = function(panel_id){
  console.log(panel_id);
  let sch_ele = document.getElementById(panel_id);
  sch_ele.classList.add("selected_panel");
  if (curr_sch_id != ''){
    document.getElementById(curr_sch_id).classList.remove("selected_panel");
  }
  curr_sch_id = panel_id;
  console.log(sch_ele.querySelector('#description').innerHTML);
  let panel_ele = document.getElementById('panel_det');
  panel_ele.querySelector("#title").innerHTML = sch_ele.querySelector("#title").innerHTML;
  panel_ele.querySelector("#room").innerHTML = sch_ele.querySelector("#room").innerHTML;
  panel_ele.querySelector("#day").innerHTML = sch_ele.querySelector("#day").innerHTML;
  panel_ele.querySelector("#start_time").innerHTML = sch_ele.querySelector("#start_time").innerHTML;
  panel_ele.querySelector("#end_time").innerHTML = sch_ele.querySelector("#end_time").innerHTML;
  panel_ele.querySelector("#panelists").innerHTML = sch_ele.querySelector("#panelists").innerHTML;
  panel_ele.querySelector("#description").innerHTML = sch_ele.querySelector("#description").innerHTML;
  panel_ele.style.display = 'inline-block';
  
  
}

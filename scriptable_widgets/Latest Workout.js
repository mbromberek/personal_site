// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: deep-green; icon-glyph: child;
/**
Get latest workout from website and image of its map to display. 
If workout date has not changed the job will re-use the old data and image. 
*/

//let widgetInput = args.widgetParameter
let widgetInput = ''
let token = '';
if (widgetInput !== null) {
  token = widgetInput;
} else {
  throw new Error("No parameters set.")
}

/**
URL is set to return one workout by the per_page parameter
The page parameter specifies to use the first page so only the latest workout
  is returned. Can change page to return older workouts.
*/
const apiURL = `https://mikebromberek.com/api/workouts?page=1&per_page=1`;

/*
var WIDGET_SIZE = (config.runsInWidget ? config.widgetFamily : "small");
*/
let widget = '';
let data = await loadActivity(apiURL, token);
let data_offline = getSavedWrktData();
let dataChange = didDataChange(data, data_offline);
if (dataChange == true){
  console.log('new data');
  let mapUrl = data['items'][0]['_links']['map_thumb'];
  let mapImg = null;
  if (mapUrl != undefined){
  	mapImg = await loadImage(mapUrl, token);
  }
	widget = await createWidget(data, mapImg);  
  //save data for offline use
	saveWrktData(data);
  saveMap(mapImg);
}else{
  console.log('old data');
  let mapImg = getSavedMap();
  widget = await createWidget(data_offline, mapImg);  
}

//console.log(data);


widget.url = "https://mikebromberek.com/workout?workout="+data['items'][0]['id'];

if (!config.runsInWidget) {
  await widget.presentMedium();
}

Script.setWidget(widget)
Script.complete()

/**
Compares wrkt_dttm between latest pulled workout and saved workout. 
This is checked to prevent re-downloading workout map when workout
  has not changed. 
*/
function didDataChange(data1, data2){
  if (data1 == '' || data1 == null || data1 == undefined){
    return false;
  }
  if (data2 == '' || data2 == null || data2 == undefined){
    return true;
  }
  let data1_dttm = data1['items'][0]['wrkt_dttm'];
  let data2_dttm = data2['items'][0]['wrkt_dttm'];
  if (data1_dttm == data2_dttm){
    return false;
  }else{
  	return true;
  }
}

/**
Save workout data as json to iCloud
*/
function saveWrktData(data) {
	let fm = FileManager.iCloud();
	let path = fm.joinPath( fm.documentsDirectory(), 'wrkt_data.json' );
		fm.writeString(path, JSON.stringify(data));
};

/**
Get saved workout data as json from iCloud
*/
function getSavedWrktData() {
	let fm = FileManager.iCloud();
	let path = fm.joinPath(fm.documentsDirectory(), 'wrkt_data.json');
  if (fm.fileExists(path)){
		let data = fm.readString( path );
		return JSON.parse(data);
  }else{
    return null;
  }
};

/**
Get saved map of workout
*/
function saveMap(img) {
  if (img == null){
    console.log('no map to save');
  }else{
		let fm = FileManager.iCloud();
		let path = fm.joinPath( fm.documentsDirectory(), 'wrkt_map.jpg' );
		fm.writeImage(path, img);
  }
};

/**
Save map of workout
*/
function getSavedMap() {
	let fm = FileManager.iCloud();
	let path = fm.joinPath(fm.documentsDirectory(), 'wrkt_map.jpg');
  if (fm.fileExists(path)){
		let img = fm.readImage( path );
		return img;
  }else{
    return null;
  }
};


/**
Gets workout using passed in URL and token
Returns workout data as JSON
*/
async function loadActivity(apiURL, token) {
  try {
    let req = new Request(apiURL);
    console.log(req.url)
    req.method = "GET"
    // construct header
    // Using Authorization-Alt for token since when I use Authorization it does not get sent in the Header
    let header = {
      Accept: "application/json",
      //Referer: req.url+'/test',
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Authorization-Alt": "Bearer " + token,
      //Origin: "https://apps.apple.com",  
    };
    req.allowInsecureRequest = false
    req.headers = header

    console.log(req)
    let data = await req.loadJSON()

    console.log('Received latest workout')
    //console.log(data);

    return data

  } catch (e) {
    data = ''
    console.error(e)
    console.log('Could not get workout')
    return data

  }
}

/**
Creates widget using passed workout data and image
*/
async function createWidget(data, mapImg) {

  let createSymbol = (name) => {
    let font = Font.mediumSystemFont(10)
    let sym = SFSymbol.named(name)
    sym.applyFont(font)

    return sym
  }

  const list = new ListWidget();

  let textColor = Color.dynamic(new Color('#333333'), new Color('#000000'));
  
  /* Background color of widget */
  let bg1 = new Color('43d9b8')
  let bg2 = new Color('76fceb')
  let gradient = new LinearGradient()
  gradient.locations = [0, 1]
  gradient.colors = [
      bg1,
      bg2
  ];
  list.backgroundGradient = gradient  

  const wrkt = data['items'][0];
  
  sectionsStack = list.addStack();
  sectionsStack.layoutHorizontally();
  sectionsStack.setPadding(0,0,0,0);
  //sectionsStack.backgroundColor= new Color('#FF0000');  
  
  detailStack = sectionsStack.addStack();
  detailStack.layoutVertically();
  detailStack.setPadding(25,1,0,1);
  //detailStack.backgroundColor= new Color('#00CCFF');

  mapStack = sectionsStack.addStack();
  mapStack.setPadding(0,0,0,0);
  mapStack.layoutHorizontally();
  //mapStack.addSpacer();
  //mapStack.size= new Size(200, 160);
  mapStack.backgroundColor= new Color('#000000CC');
    
  let dttm = formatDate(wrkt['wrkt_dttm']);
  
  listRow = detailStack.addText(dttm);
  listRow.textColor = new Color('#990000');
  listRow.minimumScaleFactor = 0.8
  listRow.font = Font.mediumRoundedSystemFont(26);

  listRow = detailStack.addText(wrkt['type'] + ': ' + wrkt['dist_mi'] + 'mi');
  listRow.textColor = textColor
  listRow.minimumScaleFactor = 0.7
  listRow.font = Font.mediumRoundedSystemFont(24);
  detailStack.addSpacer();
  
  listRow = detailStack.addText(' ');
  listRow.textColor = textColor
  listRow.minimumScaleFactor = 0.7
  listRow.font = Font.mediumRoundedSystemFont(22);


  durRow = detailStack.addStack();
  durRow.layoutHorizontally();
  
  let durImage = durRow.addImage(SFSymbol.named('clock').image);
  durImage.resizeable = false;
  durImage.imageSize = new Size(20, 20);
  
  let durTxt = durRow.addText(' ' + wrkt['duration']);
  durTxt.textColor = textColor
  durTxt.minimumScaleFactor = 0.7
  durTxt.font = Font.mediumRoundedSystemFont(22);

  let paceRow = detailStack.addStack();
  paceRow.layoutHorizontally();
  
  let paceImage = paceRow.addImage(SFSymbol.named('timer').image);
  paceImage.resizeable = false;
  paceImage.imageSize = new Size(20, 20);
  
  let paceTxt = paceRow.addText(' ' + wrkt['pace'] + ' ' + wrkt['pace_uom']);
  paceTxt.textColor = textColor
  paceTxt.minimumScaleFactor = 0.7
  paceTxt.font = Font.mediumRoundedSystemFont(22);
  paceRow.addSpacer();

	if (mapImg != null){
    let mapImage = mapStack.addImage(mapImg);
  	mapImage.resizeable = false;
  	mapImage.imageSize = new Size(160, 160);
    mapImage.containerRelativeShape = false;
    mapImage.rightAlignImage();

  } 

  return list
}

/**
Format date and time as string
*/
function formatDate(date_str) {
    let d = new Date(date_str);
    let year = d.getUTCFullYear();
    let month = (d.getUTCMonth() + 1).toString().padStart(2,'0');
    let month_str = d.toLocaleString('default',{month: 'short'});
    let day = d.getUTCDate().toString().padStart(2,'0');
    dt = [month_str, day].join(' ') + ', ';

    let hour = d.getUTCHours().toString().padStart(2,'0');
    let minute = d.getUTCMinutes().toString().padStart(2,'0');
    let second = d.getUTCSeconds().toString().padStart(2,'0');
    return dt + ' ' + hour + ':' + minute;
}

/**
Get image from passed in imgUrl and token
Returns image. 
*/
async function loadImage(imgUrl, token) {
    let req = new Request(imgUrl);
    console.log("req.url");
    //console.log(req.url);
    req.method = "GET";
    // construct header
    // Using Authorization-Alt for token since when I use Authorization it does not get sent in the Header
    let header = {
      "Authorization-Alt": "Bearer " + token,
    };
    req.allowInsecureRequest = false
    req.headers = header

    //console.log("req");
    //console.log(req)
    return await req.loadImage();
}

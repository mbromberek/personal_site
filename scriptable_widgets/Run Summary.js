// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: deep-green; icon-glyph: shoe-prints;
/**
Shows summary of running by week, month, and year
*/

//let widgetInput = args.widgetParameter
let widgetInput = ''

if (widgetInput !== null) {
  token = widgetInput;
} else {
  throw new Error("No parameters set.")
}

const apiURL = `https://mikebromberek.com/api/run_summary`;

data = await loadActivity(apiURL, token);

//console.log(data);

let widget = await createWidget(data);
widget.url = "https://mikebromberek.com/dashboard";

if (!config.runsInWidget) {
  await widget.presentSmall()
}

Script.setWidget(widget)
Script.complete()



async function loadActivity(apiURL, token) {
  try {
    let req = new Request(apiURL)
    console.log(req.url)
    req.method = "GET"
    // construct header
    // Using Authorization-Alt for token since when I use Authorization it does not get sent in the Header
    let header = {
      Accept: "application/json",
      Referer: req.url+'/test',
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Authorization-Alt": "Bearer " + token
    };
    req.allowInsecureRequest = true
    req.headers = header

    console.log(req)
    let data = await req.loadJSON()

    return data

  } catch (e) {
    data = ''
    console.error(e)
    return data

  }
}

async function createWidget(data) {

  let createSymbol = (name) => {
    let font = Font.mediumSystemFont(10)
    let sym = SFSymbol.named(name)
    sym.applyFont(font)

    return sym
  }

  const list = new ListWidget()

  // Set Colors
  let bg1 = new Color('43d9b8')
  let bg2 = new Color('76fceb')
  let bg3;
  let textColor = Color.dynamic(new Color('#444444'), new Color('#000000'));
  
  var sumDesc = ['Current Week', 'Past 7 days', 'Current Month', 'Past 30 days', 'Current Year', 'Past 365 days'];
  
  for (i =0; i<sumDesc.length; i++){
    var sumRow = data[sumDesc[i]];
    var rowDesc = sumRow['rng'].replace('Current ','').replace(' days','');
    let listRow = '';

    dist=Math.round(sumRow['tot_dist']);
    listRow = list.addText(rowDesc + ': ' + dist + ' mi');

    listRow.textColor = textColor
    listRow.minimumScaleFactor = 0.7

    if (sumRow['rng'].includes('Past')){
      listRow.font = Font.lightRoundedSystemFont(16);
	  list.addSpacer()
    }else{
      listRow.font = Font.mediumRoundedSystemFont(20);
    } 
  }
  
  
  let gradient = new LinearGradient()
  gradient.locations = [0, 1]
  gradient.colors = [
      bg1,
      bg2
  ];
  list.backgroundGradient = gradient

  return list
}

/*
loads passed in token to clipboard, then makes message in passed element visible for 2 seconds. 
*/
async function copyToken(token_full, ele_id){
    navigator.clipboard.writeText(token_full);
    document.getElementById('token_copied').style.display='inline';
    await sleep(2000);
    document.getElementById('token_copied').style.display='none';
}

/*
Pause JavaScript that called this for passed in time in milliseconds
*/
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

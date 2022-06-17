async function copyToken(ele_id){
    document.getElementById('token_copied').style.display='inline';
    await sleep(1000);
    document.getElementById('token_copied').style.display='none';
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

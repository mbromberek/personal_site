async function copyToken(token_full, ele_id){
    navigator.clipboard.writeText(token_full);
    document.getElementById('token_copied').style.display='inline';
    await sleep(2000);
    document.getElementById('token_copied').style.display='none';
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

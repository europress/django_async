function modal(url) {
    modal_w = document.getElementById("modal");
    modal_w.style.backgroundImage = "url('"+url+"')";
    modal_w.classList.toggle("hide");
}

function close_modal() {
    modal_w = document.getElementById("modal");
    modal_w.classList.toggle("hide");
}
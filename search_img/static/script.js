CLOG = true;
// -------------------------------- method 1
//function getCookie(name) {
//  const value = `; ${document.cookie}`;
//  const parts = value.split(`; ${name}=`);
//  if (parts.length === 2) return parts.pop().split(';').shift();
//}
// -------------------------------- method 2
//<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-cookie/1.4.1/jquery.cookie.min.js"
//    integrity="sha512-3j3VU6WC5rPQB4Ld1jnLV7Kd5xr+cq9avvhwqzbH/taCRNURoeEpoPBK9pDyeukwSxwRPJ8fDgvYXd6SkaZ2TA=="
//    crossorigin="anonymous" referrerpolicy="no-referrer">
//</script>
//var value = $.cookie("obligations");
//$.cookie('obligations', 'new_value');
//$.cookie('obligations', 'new_value', { expires: 14, path: '/' });
//$.removeCookie('obligations');
// -------------------------------- method 3 check name
//function check_cookie_name(name) {
//      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
//      if (match) {
//        console.log(match[2]);
//      }
//      else{
//           console.log('--something went wrong---');
//      }
//}
// -------------------------------- method 4
// function getCookie(n) {
//    let a = `; ${document.cookie}`.match(`;\\s*${n}=([^;]+)`);
//    return a ? a[1] : '';
//}
// -------------------------------- method 5
function getCookie(name) {
    function escape(s) { return s.replace(/([.*+?\^$(){}|\[\]\/\\])/g, '\\$1'); }
    const match = document.cookie.match(RegExp('(?:^|;\\s*)' + escape(name) + '=([^;]*)'));
    return match ? match[1] : null;
}
// -------------------------------- method 6 with return array possible
//function getCookie(name = '') {
//    let cookies = document.cookie;
//    let cookieStore = {};
//
//    cookies = cookies.split(";");
//
//    if (cookies[0] == "" && cookies[0][0] == undefined) {
//        return undefined;
//    }
//
//    cookies.forEach(function(cookie) {
//        cookie = cookie.split(/=(.+)/);
//        if (cookie[0].substr(0, 1) == ' ') {
//            cookie[0] = cookie[0].substr(1);
//        }
//        cookieStore[cookie[0]] = cookie[1];
//    });
//
//    return (name !== '' ? cookieStore[name] : cookieStore);
//}
// -----------------------------------------------------------------
async function cacheUpdate(url) {

// --- very costly way
//    modal_window.style.backgroundImage = "url('"+url.original+"')";
//    modal_window.classList.remove("hide");
//    const canvas = document.createElement("CANVAS");
//    canvas.width = image_tag.width;
//    canvas.height = image_tag.height;
//    const canvas_context = canvas.getContext("2d");
//    console.log('::: info image size w,h :', image_tag.width , image_tag.height)
//    canvas_context.drawImage(image_tag, 0, 0);
//    const image_raw_data = canvas.toDataURL();


//    console.log('==> <cacheUpdate(url)> income params url: ',url)
//    console.log('::: image raw data:', image_raw_data)
//    console.log('::: csrftoken:', getCookie("csrftoken"))
//    console.log('::: CSRF_TOKEN:', CSRF_TOKEN)
    const data =
        {
            id_photo: url.id,
            alt: url.alt,
            tiny: url.tiny,
            origin: url.origin,
            comma: ';'
        }

    try {
        return fetch("pixels-update-cache/",
            {
                method: "POST",
                credentials: 'same-origin',
                contentType: 'application/json; charset=utf-8',
                headers: {"X-CSRFToken": CSRF_TOKEN},
                body: JSON.stringify(data),
            }
        )
        .then(response => response.json())
        .then(data =>
            {
                console.log('==> <cacheUpdate(url)> return fetch data: ', data);
                return data;
            }
        );
    } catch (error) {
        console.log('==> <cacheUpdate(url)> fetch err, return default val: ', error);
        return url;
    }
}

//const cacheUpdate = async (url) => {
//        const response = await cacheUpdateResponse(url);
//        return response;
//}

function check_link_cached_image(url) {
    const url_obj = new URL(url, MEDIA_URL);
//    console.log("==> modal local url, checked url: ", url_obj.host, window.location.host);
//    console.log("==> modal local url == checked url: ", (url_obj.host == window.location.host));
    return (url_obj.host == window.location.host);
}

function getFuncName() {
    return getFuncName.caller.name;
}

function clog(message, typeMess="i") {
    if (!CLOG) {
        return;
    }

    title = "==> ";
    if (typeMess == "e") {
        title = title + "ERR";
    } else if (typeMess == "l") {
        title = title + "LOG";
    } else {
        title = title + "INFO";
    }

    if (clog.caller == undefined) {
        callerFunc = "main func";
    } else {
        callerFunc = clog.caller.name;
    }
    console.log(title + " in <" + callerFunc + "> :", message);
}

function setBackgroundToElement( element, url ) {

    const imageTag = new Image();
    imageTag.crossOrigin = "Anonymous";
    absoluteUrl = MEDIA_URL + url;

    imageTag.addEventListener('load', function() {
        element.style.backgroundImage = "url('"+ absoluteUrl +"')";
        element.classList.remove("hide");
    }, { once: true });
    imageTag.src = absoluteUrl;
}

function loadingAnimateShow(toParent, action='stop') {
    className = "loading-icon"
    el = toParent.querySelector("span");
    (action == 'start') ? el.classList.add(className) : el.classList.remove(className)
}

async function modal(htmlCaller) {

//    clog("==> modal MEDIA_URL: " + MEDIA_URL);
    const modalWindow = document.getElementById("modal");
    const imageId = htmlCaller.dataset.jsonId;
//    clog("imageId: " + imageId);
    const imageData = document.getElementById(imageId);
    const imageDataJson = JSON.parse(imageData.textContent);
//    clog("imageData: " + JSON.stringify(imageData));

    loadingAnimateShow(htmlCaller, 'start');

    if (!check_link_cached_image(imageDataJson.origin)) {
        clog("==> <modal> image not cached!");
        await cacheUpdate(imageDataJson)
        .then( data => {
            imageDataJson.origin = data.origin;
            imageData.textContent = JSON.stringify(imageDataJson);
//            clog("fetch data: " + data);
            setBackgroundToElement(modalWindow, imageDataJson.origin );
            loadingAnimateShow(htmlCaller, 'stop');
            htmlCaller.getElementsByTagName("i")[0].classList.remove("un_cached");
            htmlCaller.getElementsByTagName("i")[0].classList.add("cached");
        })
    } else {
        setBackgroundToElement(modalWindow, imageDataJson.origin );
        loadingAnimateShow(htmlCaller, 'stop');
    }
}

function close_modal(modalWindow) {
    modalWindow.classList.add("hide");
}

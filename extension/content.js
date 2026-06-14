function sendTitleToAcsense() {
    try {
        fetch("http://127.0.0.1:5000/youtube-activity", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                title: document.title,
                url: location.href,
            }),
        });
    } catch (error) {
        console.log(error);
    }
}

let lastTitle = "";

// check every seconds if the title has change, only then we'll send a request
setInterval(() => {
    if (document.title != lastTitle) {
        lastTitle = document.title;

        sendTitleToAcsense();
    }
}, 1000);

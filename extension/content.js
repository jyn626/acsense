function sendTitleToAcsense() {
    try {
        fetch("http://localhost:5000/activity", {
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

setInterval(() => {
    if (document.title != lastTitle) {
        lastTitle = document.title;

        getTabTitle();
    }
}, 2000);

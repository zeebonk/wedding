(function() {
    var $ = document.querySelector.bind(document);
    var $$ = document.querySelectorAll.bind(document);

    function showPage(page) {
        var pages = $$(".page");
        for (var i = 0; i < pages.length; i++) {
            pages[i].style.display = "none";
        }
        $("#" + page).style.display = "block";
    }

    function send(ws, data) {
        ws.send(JSON.stringify(data));
    }

    showPage("auth-code");

    var host = "ws://ws.250120.gs";
    if (window.location.host.startsWith("localhost")) {
        host = "ws://localhost:8000";
    }

    var ws = new WebSocket(host);

    $("#auth-code form").onsubmit = function() {
        send(ws, {
            type: "auth-code",
            code: parseInt($("#auth-code input[name=code]").value)
        });
        return false;
    };

    $("#count-code form").onsubmit = function() {
        send(ws, {
            type: "count-code",
            code: parseInt($("#count-code input[name=code]").value)
        });
        return false;
    };

    $("#questions-form form").onsubmit = function() {
        send(ws, {
            type: "question-answers",
            name: $("#questions-form input[name=name]").value,
            age: parseInt($("#questions-form input[name=age]").value)
        });
        return false;
    };

    ws.onmessage = function(event) {
        console.log(event);
        var data = JSON.parse(event.data);
        console.log(data);
        var type = data["type"];

        if (type == "auth-code-ok") {
            showPage("questions-form");
        } else if (type == "auth-code-invalid") {
            $("#auth-code .invalid-feedback").style.display = "block";
            showPage("auth-code");
        } else if (type == "lobby-count") {
            $("#lobby .answering").innerText = data["connected"] - data["done"];
            $("#lobby .waiting").innerText = data["done"] - 1;
            showPage("lobby");
        } else if (type == "countdown") {
            var count = data["count"];
            showPage("countdown");
            $("#countdown .count").innerText = count;
            window.navigator.vibrate(200);
        } else if (type == "show-count-code") {
            $("#count-code").style.background = data["color"];
            showPage("count-code");
        } else if (type == "count-code-ok") {
            console.warn("COUNT CODE OK, DONE");
        } else if (type == "count-code-invalid") {
            $("#count-code .invalid-feedback").style.display = "block";
            showPage("count-code");
        } else if (type == "wait-for-groups") {
            $("#wait-for-groups .total").innerText = data["total"];
            $("#wait-for-groups .done").innerText = data["done"];
            showPage("wait-for-groups");
        } else if (type == "show-success") {
            showPage("success");
        } else if (type == "reset") {
            window.location = "";
        }
    };
})();

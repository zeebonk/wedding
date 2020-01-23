(function() {
    var $ = document.querySelector.bind(document);
    var $$ = document.querySelectorAll.bind(document);

    function showPage(pageID) {
        var pages = $$(".page");
        for (var i = 0; i < pages.length; i++) {
            var page = pages[i];
            if (page.id != pageID) {
                page.style.display = "none";
                page.style.background = "none";

                var inputs = page.querySelectorAll("input[type=text], input[type=number]");
                for (var j = 0; j < inputs.length; j++) {
                    var input = inputs[j];
                    input.value = "";
                }
            }
        }
        $("#" + pageID).style.display = "block";
    }

    function send(ws, data) {
        ws.send(JSON.stringify(data));
    }

    showPage("connect");

    var host = "ws://ws.250120.gs";
    if (window.location.host.startsWith("localhost")) {
        host = "ws://localhost:8000";
    }

    var ws = new WebSocket(host);

    ws.onclose = function(event) {
        setTimeout(function() {
            window.location = "";
        }, 1000);
    };

    ws.onopen = function(event) {
        showPage("teaser");
        ws.onclose = function(event) {
            window.location = "";
        };
    };

    $("#auth-code form").onsubmit = function() {
        send(ws, {
            type: "auth-code",
            code: $("#auth-code input[name=code]").value
        });
        return false;
    };

    $("#count-code form").onsubmit = function() {
        send(ws, {
            type: "code",
            code: $("#count-code input[name=code]").value
        });
        return false;
    };

    $("#questions-form form").onsubmit = function() {
        send(ws, {
            type: "question-answers",
            name: $("#questions-form input[name=name]").value,
            age: $("#questions-form input[name=age]").value
        });
        return false;
    };

    $("#total-age form").onsubmit = function() {
        send(ws, {
            type: "code",
            code: $("#total-age input[name=code]").value
        });
        return false;
    };

    $("#name-order form").onsubmit = function() {
        send(ws, {
            type: "code",
            code: $("#name-order input[name=code]").value
        });
        return false;
    };

    $("#slow-dance form").onsubmit = function() {
        send(ws, {
            type: "code",
            code: $("#slow-dance input[name=code]").value
        });
        return false;
    };

    function setColors(id, colors) {
        var element = $("#" + id);
        var background =
            "repeating-linear-gradient(45deg, " +
            colors[0] +
            ", " +
            colors[0] +
            " 33%, " +
            colors[1] +
            " 33%, " +
            colors[1] +
            " 67%)";
        element.style.background = background;
        element.style.color = colors[3];
    }

    ws.onmessage = function(event) {
        console.log(event);
        var data = JSON.parse(event.data);
        console.log(data);
        var type = data["type"];

        if (type == "show-teaser") {
            showPage("teaser");
        } else if (type == "show-auth-code") {
            showPage("auth-code");
        } else if (type == "auth-code-ok") {
            showPage("questions-form");
        } else if (type == "auth-code-invalid") {
            $("#auth-code input").classList.add("is-invalid");
            showPage("auth-code");
        } else if (type == "lobby-count") {
            $("#lobby .answering").innerText = data["connected"] - data["done"];
            $("#lobby .waiting").innerText = data["done"] - 1;
            showPage("lobby");
        } else if (type == "countdown") {
            $("#countdown .count").innerText = data["count"];
            $("#countdown .round").innerText = data["round"] + 1;
            showPage("countdown");
            window.navigator.vibrate(200);
        } else if (type == "show-count-code") {
            setColors("count-code", data["color"]);
            showPage("count-code");
        } else if (type == "count-code-invalid") {
            $("#count-code input").classList.add("is-invalid");
            showPage("count-code");
        } else if (type == "wait-for-groups") {
            $("#wait-for-groups .total").innerText = data["total"];
            $("#wait-for-groups .done").innerText = data["done"];
            showPage("wait-for-groups");
        } else if (type == "show-success") {
            $("#success .round-finished").innerText = data["round"];
            $("#success .round-next").innerText = data["round"] + 1;
            showPage("success");
        } else if (type == "show-total-age") {
            setColors("total-age", data["color"]);
            showPage("total-age");
        } else if (type == "total-age-invalid") {
            $("#total-age input").classList.add("is-invalid");
            showPage("total-age");
        } else if (type == "show-name-order") {
            setColors("name-order", data["color"]);
            showPage("name-order");
        } else if (type == "name-order-invalid") {
            $("#name-order input").classList.add("is-invalid");
            showPage("name-order");
        } else if (type == "show-slow-dance") {
            setColors("slow-dance", data["color"]);
            showPage("slow-dance");
        } else if (type == "slow-dance-code-invalid") {
            $("#slow-dance input").classList.add("is-invalid");
            showPage("slow-dance");
        } else if (type == "team-progress") {
            $("#team-progress .total").innerText = data["n_users"];
            $("#team-progress .done").innerText = data["n_done_users"];
            showPage("team-progress");
        } else if (type == "show-the-end") {
            showPage("the-end");
        } else if (type == "reset") {
            window.location = "";
        }
    };
})();

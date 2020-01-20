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

    $("#total-age form").onsubmit = function() {
        send(ws, {
            type: "total-age",
            code: parseInt($("#total-age input[name=code]").value)
        });
        return false;
    };

    $("#name-order form").onsubmit = function() {
        send(ws, {
            type: "name-order",
            code: parseInt($("#name-order input[name=code]").value)
        });
        return false;
    };

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
            $("#count-code").style.background = data["color"][0];
            $("#count-code").style.color = data["color"][1];
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
            $("#total-age").style.background = data["color"][0];
            $("#total-age").style.color = data["color"][1];
            showPage("total-age");
        } else if (type == "total-age-invalid") {
            $("#total-age input").classList.add("is-invalid");
            showPage("total-age");
        } else if (type == "show-name-order") {
            $("#name-order").style.background = data["color"][0];
            $("#name-order").style.color = data["color"][1];
            showPage("name-order");
        } else if (type == "name-order-invalid") {
            $("#name-order input").classList.add("is-invalid");
            showPage("name-order");
        } else if (type == "team-progress") {
            $("#team-progress .total").innerText = data["n_users"];
            $("#team-progress .done").innerText = data["n_done_users"];
            showPage("team-progress");
        } else if (type == "reset") {
            window.location = "";
        }
    };
})();

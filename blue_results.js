var websocket;
var accessCode = "0000-V-r3FEwc";

function login() {
    websocket = new WebSocket("wss://ecsrv.orcah.org:443");
  websocket.onopen = function(event) {
    console.log("Connected to server");
    websocket.send(JSON.stringify({api: "Login", operation: "login", accessCode: accessCode}));
  };
}


function initTriple() {
  login();
    websocket.onmessage = function (event) {
      data = JSON.parse(event.data);
        if (data.api == "Livestream_Results") {
            console.log(data);
            document.querySelector('#red1').innerHTML = data.b_rank;
            document.querySelector('#red2').innerHTML = data.blue;
            document.querySelector('#red3').innerHTML = data.b_name;
            document.querySelector('#red4').innerHTML = data.b_state;
      }
      else {
          console.log(data.api)
      }
  };
}

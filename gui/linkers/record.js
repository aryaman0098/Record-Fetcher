const {PythonShell} = require('python-shell')
const path = require("path")


function get_weather() {

  const city = document.getElementById("city").value
  //document.getElementById("head").innerHTML = city;
  
  const options = {
    scriptPath : path.join(__dirname, '/../engine/'),
    args : [city]
  }

  const pyshell = new PythonShell('weather_engine.py', options);


  pyshell.on('message', message => {
    //swal(message);
    document.getElementById("weather").innerHTML = message;
    document.getElementById("city").value = "";
  })
}



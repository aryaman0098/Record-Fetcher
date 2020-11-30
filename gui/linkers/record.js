const {PythonShell} = require('python-shell')
const path = require("path")


const asyncLocalStorage = {
    setItem: function (key, value) {
        return Promise.resolve().then(function () {
            localStorage.setItem(key, value);
        });
    },
    getItem: function (key) {
        return Promise.resolve().then(function () {
            return localStorage.getItem(key);
        });
    }
};

function genTable(obj) {
  let table = document.createElement("table")
  let header = table.createTHead();
  header.className="thead-light";
  let row = header.insertRow(0);
  row.insertCell(0).innerHTML = "<strong> Field </strong>";
  row.insertCell(1).innerHTML = "<strong> Value </strong>";
  // row = table.insertRow(1)

  let keys = Object.keys(obj)
  let tbody= table.createTBody()
  for (let i = 0; i < keys.length; i++) {
    row = tbody.insertRow(i)
    row.insertCell(0).innerHTML = keys[i];
    row.insertCell(1).innerHTML = obj[keys[i]];
  }
  table.className="table table-striped table-light";
  let body = document.querySelector("#dict");
  //let body=document.getElementById('dict');
  body.append(table); 

  console.log(table)
  console.log(table.innerHTML)
  return table

}


function main(){
  const name = document.getElementById("name").value
  const lang = document.getElementById("lang").value
  let email='0'
  let phone='0'
  let academic='0'
  let other='0'

  if (document.getElementById('email').checked) {
    email='1'
  }
  if (document.getElementById('phone').checked) {
    phone='1'
  }
  if (document.getElementById('academic').checked) {
    academic='1'
  }
  if (document.getElementById('other').checked) {
    other='1'
  }
  asyncLocalStorage.getItem('status').then(function (status) {
    const options = {
      scriptPath : path.join(__dirname, '/../engine/'),
      args : [name,lang,email,phone,academic,other,status]
    }

    const pyshell = new PythonShell('client.py', options);


    pyshell.on('message', message => {
      //console.log(message.slice(0,10))
      //console.log(message)
      let msg=JSON.parse(message)
      //console.log(typeof(msg))
      console.log(msg)
      document.getElementById('dict').innerHTML="";
      if('first' in msg){
        //let sent=msg.first.name+" "+msg.second.name
        document.getElementById("dict").innerHTML +="Similar results to your search"+"<br>";
        if ('gen' in msg.first) {
          document.getElementById("dict").innerHTML += "Sorry! You are not Authorized to view the Record of "+msg.first.name+'<br>';
        }
        else {
          document.getElementById("dict").appendChild(genTable(msg.first));
        }
        if ('gen' in msg.second) {
          document.getElementById("dict").innerHTML += "Sorry! You are not Authorized to view the Record of "+msg.second.name+'<br>';;
        }
        else {
          document.getElementById("dict").appendChild(genTable(msg.second));
        }
      }
      else if ('gen' in msg) {
        document.getElementById("dict").innerHTML += "Sorry! You are not Authorized to view the Record of "+msg.name+'<br>';
      }
      else {
        document.getElementById("dict").appendChild( genTable(msg));
      }
    })
  })

}



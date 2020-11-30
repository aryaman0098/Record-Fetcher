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


window.onload = function() {
  check();
};

function check() {
	asyncLocalStorage.getItem('status').then(function (status) {
		if(status && status==1){
			document.getElementById("logout").style.display = "block"
			document.getElementById("login").style.display = "none"
		}
		else{
			document.getElementById("logout").style.display = "none";
			document.getElementById("login").style.display = "block"
			document.getElementById("name").value = "";
			document.getElementById("password").value = "";
		}
	})
}

function login() {
	asyncLocalStorage.getItem('status').then(function (status) {
		if(status && status==1){
			swal('Already Logged In')
			document.getElementById("logout").style.display = "block";
			document.getElementById("login").style.display = "none"
		}
		else{
			const name = document.getElementById("name").value
			const password = document.getElementById("password").value
			if(name=="Admin" && password=="1234"){
				asyncLocalStorage.setItem('status', '1').then(function () {
			    	//swal('Logged In')
					document.getElementById("login").style.display = "none"
					document.getElementById("logout").style.display = "block";
					document.getElementById("name").value = "";
					document.getElementById("password").value = "";
					document.getElementById("change").href="record.html"; 
				})
			}
			else{
				swal('Invalid Credentials')
				document.getElementById("logout").style.display = "none";
				document.getElementById("login").style.display = "block"
				document.getElementById("name").value = "";
				document.getElementById("password").value = "";
			}
		}
	})
}

function logout() {
	asyncLocalStorage.getItem('status').then(function (status) {
		if(status && status==1){
			asyncLocalStorage.setItem('status', '0').then(function () {
			    swal('Logged Out')
			    document.getElementById("logout").style.display = "none";
				document.getElementById("login").style.display = "block"
			})
		}
		else{
			swal('Already Logged Out')
			document.getElementById("logout").style.display = "none";
			document.getElementById("login").style.display = "block"
		}
	})
}


 



const username = document.querySelector('#username_input');
const passwd = document.querySelector('#password_input');
const confirmPasswd = document.querySelector('#password_confirm');

function fillUserData() {
    let headerData = new Headers();

    let authToken = sessionStorage.getItem("authtoken");
    if(authToken){
        headerData.set("authtoken", authToken);
    }

    fetch('/api/user/myinfo', {
        method: 'POST',
        headers: headerData,
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        username.value = resBody["username"];
    }).catch((error) => {
        console.log('[Error]fillUserData:', error);
    });
}

window.addEventListener('load', fillUserData);

function checkPw() {
    if (passwd.value !== confirmPasswd.value) {
        alert("비밀번호가 일치하지 않습니다.");
        return false;
    }
    if (passwd.value.length < 5) {
        alert("비밀번호는 5자 이상이어야 합니다.");
        return false;
    }
    return true;
}

function onSubmitHandler() {
    let pwValid =  checkPw();

    if(pwValid){
        let headerData = new Headers();

        let authToken = sessionStorage.getItem("authtoken");
        if(authToken){
            headerData.set("authtoken", authToken);
        }

        let formData = new FormData();

        formData.set("username", username.value);
        formData.set("passwd", passwd.value);

        fetch('/api/user/update', {
            method: 'POST',
            headers: headerData,
            body: formData
        }).then((response) => {
            let url = '/home';
            window.location.replace(url);
        }).catch((error) => {
            console.log('[Error]signup:', error);
        });
    }
}

function onProfileView() {
let pwValid = checkPw();

    if (pwValid) {
        window.location.href = '/health';
    }
}

const profileButton = document.querySelector('#profile_button');
profileButton.addEventListener('click', onProfileView);

const submitButton = document.querySelector('#submit_button');
submitButton.addEventListener('click', onSubmitHandler);

function onCancelHandler() {
    history.back();
}
const cancelButton = document.querySelector('#cancel_button');
cancelButton.addEventListener('click', onCancelHandler);
const email = document.querySelector('#email_input');
const passwd = document.querySelector('#password_input');
const errorMessageDiv = document.querySelector('#login_error_message');

function onSubmitHandler() {

    let formData = new FormData();

    formData.set("email", email.value);
    formData.set("passwd", passwd.value);

    fetch('/api/user/signin', {
        method: 'POST',
        body: formData
    }).then((response) => {
        if (!response.ok) {
            throw new Error('아이디가 없거나 비밀번호가 일치하지 않습니다.');
        }
        return response.json();
    }).then((resBody) => {
        window.sessionStorage.setItem("authtoken", resBody["authtoken"]);
        window.sessionStorage.setItem("user_id", resBody["user_id"]);
        window.sessionStorage.setItem("username", resBody["username"]);
        let url = '/home';
        window.location.replace(url);
    }).catch((error) => {
        console.log('[Error]signin:', error);
        errorMessageDiv.textContent = error.message;
        rrorMessageDiv.classList.remove('d-none');
    });
}

let submitButton = document.querySelector('#submit_button');
submitButton.addEventListener('click', onSubmitHandler);

function onCancelHandler() {
    let url = '/home';
    window.location.replace(url);
}

let cancelButton = document.querySelector('#cancel_button');
cancelButton.addEventListener('click', onCancelHandler);
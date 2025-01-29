const username = document.querySelector('#username_input');
const email = document.querySelector('#email_input');
const passwd = document.querySelector('#password_input');
const confirmPasswd = document.querySelector('#password_confirm');

function checkPw() {
    return (passwd.value.length >= 5) && (passwd.value === confirmPasswd.value);
}

function onSubmitHandler() {
    let pwValid = checkPw();

    if(!pwValid) {
    alert("비밀번호가 일치하지 않거나 5자리 미만입니다.");
    return;
    }

    let formData = new FormData();

    formData.set("username", username.value);
    formData.set("email", email.value);
    formData.set("passwd", passwd.value);

    fetch('/api/user/signup', {
        method: 'POST',
        body: formData
    }).then((response) => {
        if(response.ok) {
            alert("회원가입 성공! 홈페이지로 이동합니다.");
            window.location.replace('/home');
        } else {
            response.json().then(data => {
                alert(data.message); // 서버에서 반환한 오류 메시지를 표시
            });
        }
    }).catch((error) => {
        console.log('[Error]signup:', error);
        alert('회원가입 중 오류가 발생했습니다.');
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
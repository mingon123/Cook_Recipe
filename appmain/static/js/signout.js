document.getElementById('signout_link').addEventListener('click', function () {
    fetch('/api/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        if (resBody.success) {
            window.location.reload();
        } else {
            alert('로그아웃에 실패했습니다.');
        }
    }).catch((error) => {
        console.log('[Error]logout():', error);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const authToken = sessionStorage.getItem("authtoken");
    if (authToken) {
        fetchHealthInfo(authToken);
    }

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateLocalStorage);
    });
});

function fetchHealthInfo(authToken) {
    fetch('/api/user/health', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + authToken
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('인증 실패');
            } else {
                throw new Error('서버 오류: ' + response.status);
            }
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.getElementById('height').value = data.healthInfo.height;
            document.getElementById('weight').value = data.healthInfo.weight;
            document.getElementById('allergies').value = data.healthInfo.allergies;

            document.getElementById('weight_loss').checked = data.healthInfo.weight_loss;
            document.getElementById('diabetes').checked = data.healthInfo.diabetes;
            document.getElementById('high_bp').checked = data.healthInfo.high_bp;
            document.getElementById('cholesterol').checked = data.healthInfo.cholesterol;

            // Update checkboxes based on localStorage values
            const diabetes = localStorage.getItem('diabetes') === 'true';
            document.getElementById('diabetes').checked = diabetes;

            const high_bp = localStorage.getItem('high_bp') === 'true';
            document.getElementById('high_bp').checked = high_bp;

            const cholesterol = localStorage.getItem('cholesterol') === 'true';
            document.getElementById('cholesterol').checked = cholesterol;
        } else {
            console.error('정보를 불러오는 데 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateLocalStorage() {
    const diabetes = document.getElementById('diabetes').checked;
    localStorage.setItem('diabetes', diabetes);

    const high_bp = document.getElementById('high_bp').checked;
    localStorage.setItem('high_bp', high_bp);

    const cholesterol = document.getElementById('cholesterol').checked;
    localStorage.setItem('cholesterol', cholesterol);
}

function calculateBMI() {
    const height = document.getElementById('height').value / 100;
    const weight = document.getElementById('weight').value;
    if (height > 0 && weight > 0) {
        const bmi = weight / (height * height);
        document.getElementById('bmiResult').textContent = `BMI: ${bmi.toFixed(2)}`;
    }
}

function submitHealthInfo() {
    const authToken = sessionStorage.getItem("authtoken");
    if (!authToken) {
        console.error('인증 토큰이 없습니다.');
        return;
    }

    const height = document.getElementById('height').value;
    const weight = document.getElementById('weight').value;
    const allergies = document.getElementById('allergies').value;

    const weight_loss = document.getElementById('weight_loss').checked;
    const diabetes = document.getElementById('diabetes').checked || localStorage.getItem('diabetes') === 'true';
    const high_bp = document.getElementById('high_bp').checked || localStorage.getItem('high_bp') === 'true';
    const cholesterol = document.getElementById('cholesterol').checked || localStorage.getItem('cholesterol') === 'true';

    calculateBMI();

    fetch('/api/user/health', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ height, weight, allergies, weight_loss, diabetes, high_bp, cholesterol })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('인증 실패');
            } else {
                throw new Error('서버 오류: ' + response.status);
            }
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('건강 정보가 성공적으로 저장되었습니다.');
        } else {
            alert('정보 저장에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('정보 저장에 실패했습니다.');
    });
}

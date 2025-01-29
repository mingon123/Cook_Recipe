const recentArticlesDiv = document.querySelector('#recent_articles_div');
const searchButton = document.querySelector('#search_button');
const searchResultDiv = document.querySelector('#search_result_div');
const noDairyCheckbox = document.getElementById('no_dairy');
const vegetarianCheckbox = document.getElementById('vegetarian');
const veganCheckbox = document.getElementById('vegan');
const nutCheckbox = document.getElementById('nut');

//첫화면 레시피
function displayRecentArticles(articles) {
    const container = document.getElementById('recent_articles_div');
    container.innerHTML = '';

    articles.forEach(article => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card mt-2';

        const articleElement = `
            <h5 class="card-header" style="background-color: #c0c0c0;">
                <a class="link-primary text-decoration-none" href="/display_article/${article.articleNo}">
                    ${article.recipeName}
                </a>
            </h5>
            <div class="card-body">
                <p class="card-text">재료: ${article.ingredients}</p><br>
                <p class="card-text">조리 방법: ${article.cookingMethod} &nbsp;&nbsp; 요리 종류: ${article.cuisineType}</p>
                <p class="card-text"><strong>영양(1회 제공량당)</strong><br> 열량: ${article.calories}kcal, 탄수화물: ${article.carbohydrates}g, 단백질: ${article.protein}g, 지방: ${article.fat}g, 나트륨: ${article.sodium}mg</p>
            </div>
        `;

        cardDiv.innerHTML = articleElement;
        container.appendChild(cardDiv);
    });
}

function getRecentArticles() {
    fetch('/api/article/recent', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        displayRecentArticles(resBody["articles"]);
    }).catch((error) => {
        console.log('[Error]getRecentArticles():', error);
    });
}

function fetchRecentArticles() {
    fetch('/api/article/recent', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        displayRecentArticles(resBody["articles"]);
    }).catch((error) => {
        console.log('[Error]fetchRecentArticles():', error);
    });
}


//상세페이지
function displaySearchResults(articles) {
    articles.forEach((article) => {
        let articleNo = article["articleNo"];
        let title = article["recipeName"];
        let desc = article["ingredients"];
        let cookingMethod = article["cookingMethod"];
        let cuisineType = article["cuisineType"];
        let calories = article["calories"];
        let carbohydrates = article["carbohydrates"];
        let protein = article["protein"];
        let fat = article["fat"];
        let sodium = article["sodium"];

        let cardDiv = document.createElement('div');
        cardDiv.className = 'card mt-2';

        let articleElement = `
            <h5 class="card-header" style="background-color: #c0c0c0;">
                <a class="link-primary text-decoration-none" href="/display_article/${articleNo}">
                    ${title}
                </a>
            </h5>
            <div class="card-body">
                <p class="card-text">재료: ${desc}</p><br>
                <p class="card-text">조리 방법: ${cookingMethod} &nbsp;&nbsp; 요리 종류: ${cuisineType}</p>
                <p class="card-text"><strong>영양(1회 제공량당)</strong><br> 열량: ${calories}kcal, 탄수화물: ${carbohydrates}g, 단백질: ${protein}g, 지방: ${fat}g, 나트륨: ${sodium}mg</p>
            </div>
        `;

        cardDiv.innerHTML = articleElement;
        searchResultDiv.appendChild(cardDiv);
    });

    let vacantDiv = document.createElement('div');
    vacantDiv.className = 'card mt-5';
    vacantDiv.style = 'border: None;';
    searchResultDiv.appendChild(vacantDiv);
}

function handleLoginResponse(response) {
    const authToken = response.authToken;
    localStorage.setItem('jwtToken', authToken);
}

function getJWTToken() {
    return localStorage.getItem('jwtToken');
}

function checkJWTToken() {
    const jwtToken = getJWTToken();
    return jwtToken !== null;
}

//검색
function searchArticle() {
    const authToken = sessionStorage.getItem('authtoken');

    if (!authToken) {
        alert('로그인 후에 검색할 수 있습니다.');
        window.location.href = '/signin';
        return;
    }

    let ingredients = document.getElementById('ingredients').value;
    let excludedIngredients = document.getElementById('excluded_ingredients').value;
    let noDairy = noDairyCheckbox.checked ? true : false;
    let vegetarian = vegetarianCheckbox.checked ? true : false;
    let vegan = veganCheckbox.checked ? true : false;
    let nut = nutCheckbox.checked ? true : false;
    let cuisineType = document.getElementById('cuisine_type').value;

    ingredients = ingredients.trim() !== '' ? ingredients : '';
    excludedIngredients = excludedIngredients.trim() !== '' ? excludedIngredients : '';

    let formData = new FormData();
    formData.set("searchKeyword", ingredients);
    formData.set("excludedIngredients", excludedIngredients);
    formData.set("noDairy", noDairy);
    formData.set("vegetarian", vegetarian);
    formData.set("vegan", vegan);
    formData.set("nut", nut);
    formData.set("cuisineType", cuisineType);

    fetch('/api/article/search', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        recentArticlesDiv.parentElement.remove();
        const prevSR = searchResultDiv.querySelectorAll('.card');

        if (prevSR.length > 0) {
            prevSR.forEach((prevItem) => {
                prevItem.remove();
            });
        }

        if (resBody["success"] === true) {
            displaySearchResults(resBody["articles"]);
        } else {
            let cardDiv = document.createElement('div');
            cardDiv.className = 'card mt-2 text-center';
            cardDiv.style = 'border: None;';

            const noSR = '<p>죄송합니다. 결과를 찾을 수 없습니다.</p>';

            cardDiv.innerHTML = noSR;
            searchResultDiv.appendChild(cardDiv);
        }
    }).catch((error) => {
        console.log('[Error]searchArticle():', error);
    });
}

searchButton.addEventListener('click', searchArticle);
noDairyCheckbox.addEventListener('change', searchArticle);
vegetarianCheckbox.addEventListener('change', searchArticle);
veganCheckbox.addEventListener('change', searchArticle);
nutCheckbox.addEventListener('change', searchArticle);
const recentArticlesDiv = document.querySelector('#recent_articles_div');
const searchButton = document.querySelector('#search_button');
const searchResultDiv = document.querySelector('#search_result_div');
const noDairyCheckbox = document.getElementById('no_dairy');
const vegetarianCheckbox = document.getElementById('vegetarian');
const veganCheckbox = document.getElementById('vegan');
const nutCheckbox = document.getElementById('nut');
const recipeNameInput = document.getElementById('recipe_name');
const cuisineTypeInput = document.getElementById('cuisine_type');

//첫화면 레시피
function displayRecentArticles(articles) {
    const container = document.getElementById('recent_articles_div');
    container.innerHTML = '';

    articles.forEach(article => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card mt-2';

        const image = article["image"];
        const ingredients = article["ingredients"].split(' ').join(', ');

        const articleElement = `
            <div class="card-header" style="background-color: #c0c0c0;">
                <h5 class="card-title">
                    <a class="link-primary text-decoration-none" href="/display_article/${article.articleNo}">
                        ${article.recipeName}
                    </a>
                </h5>
            </div>
            <div class="row g-0">
                <div class="col-md-4">
                    ${image ? `<img src="${image}" alt="레시피 이미지" class="img-fluid rounded-start">` : ''}
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <p class="card-text">재료: ${ingredients}</p>
                    </div>
                </div>
            </div>
        `;

        cardDiv.innerHTML = articleElement;
        container.appendChild(cardDiv);
    });

    const vacantDiv = document.createElement('div');
    vacantDiv.className = 'card mt-5';
    vacantDiv.style = 'border: None;';
    container.appendChild(vacantDiv);

    container.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = this.href;
        });
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


//검색 후 레시피
function displaySearchResults(articles) {
    searchResultDiv.innerHTML = '';

    articles.forEach((article) => {
        let articleNo = article["articleNo"];
        let title = article["recipeName"];
        let ingredients = article["ingredients"].split(' ').join(', ');
        let image = article["image6"] || article["image5"] || article["image4"] || article["image3"] || article["image2"] || article["image1"];

        let cardDiv = document.createElement('div');
        cardDiv.className = 'card mt-2';

        let articleElement = `
            <div class="card-header" style="background-color: #c0c0c0;">
                <h5 class="card-title">
                    <a class="link-primary text-decoration-none" href="/display_article/${articleNo}">
                        ${title}
                    </a>
                </h5>
            </div>
            <div class="row g-0">
                <div class="col-md-4">
                    <img src="${image}" alt="레시피 이미지" class="img-fluid rounded-start">
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <p class="card-text">재료: ${ingredients}</p>
                    </div>
                </div>
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

function setCuisineType(type, element) {
    if (cuisineTypeInput) {
        if (cuisineTypeInput.value === type) {
            cuisineTypeInput.value = '';
            element.classList.remove('selected');
        } else {
            cuisineTypeInput.value = type;
            document.querySelectorAll('.clr li').forEach(li => li.classList.remove('selected'));
            element.classList.add('selected');
        }
    } else {
        console.error("Cuisine type input element is missing!");
    }
}



//검색
function searchArticle() {
    const authToken = sessionStorage.getItem('authtoken');

    if (!authToken) {
        if (!alertDisplayed) {
            alert('로그인 후에 검색할 수 있습니다.');
            window.location.href = '/signin';
        }
        return;
    }

    let ingredients = document.getElementById('ingredients').value;
    let excludedIngredients = document.getElementById('excluded_ingredients').value;
    let noDairy = noDairyCheckbox.checked ? true : false;
    let vegetarian = vegetarianCheckbox.checked ? true : false;
    let vegan = veganCheckbox.checked ? true : false;
    let nut = nutCheckbox.checked ? true : false;
    let cuisineType = cuisineTypeInput ? cuisineTypeInput.value : '';
    let recipeName = recipeNameInput ? recipeNameInput.value.trim() : '';

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
    formData.set("recipeName", recipeName);

    fetch(`/api/article/search?page=${currentPage}&limit=${articlesPerPage}`, {
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
            updatePaginationControls(resBody["totalArticles"]);
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

document.addEventListener('DOMContentLoaded', function () {
    const scrollToSearchButton = document.querySelector('#start-search-btn'); // 요리 레시피 찾아보기 버튼
    const searchSection = document.querySelector('#search-section'); // 검색 섹션
    const welcomeSection = document.querySelector('#welcome-section'); // 환영 섹션

    scrollToSearchButton.addEventListener('click', function (event) {
        event.preventDefault(); // 기본 동작 방지
        welcomeSection.style.display = 'none'; // 환영 섹션 숨기기
        searchSection.style.display = 'block'; // 검색 섹션 표시
    });
});

//document.addEventListener('DOMContentLoaded', function () {
//    const scrollToSearchButton = document.querySelector('#start-search-btn'); // 요리 레시피 찾아보기 버튼
//    const searchSection = document.querySelector('#search-section'); // 검색 섹션
//
//    scrollToSearchButton.addEventListener('click', function (event) {
//        event.preventDefault(); // 기본 동작 방지
//        searchSection.scrollIntoView({ behavior: 'smooth' }); // 검색 섹션으로 스크롤
//    });
//});



searchButton.addEventListener('click', searchArticle);
noDairyCheckbox.addEventListener('change', searchArticle);
vegetarianCheckbox.addEventListener('change', searchArticle);
veganCheckbox.addEventListener('change', searchArticle);
nutCheckbox.addEventListener('change', searchArticle);

window.onload = fetchRecentArticles;


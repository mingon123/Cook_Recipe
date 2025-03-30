let currentPage = 1;
const articlesPerPage = 10;
const pagesPerGroup = 10;

function paginate(array, page_size, page_number) {
    return array.slice((page_number - 1) * page_size, page_number * page_size);
}

function updatePaginationControls(totalArticles) {
    const totalPages = Math.ceil(totalArticles / articlesPerPage);
    const paginationControls = document.getElementById('pagination_controls');
    paginationControls.innerHTML = '';

    const currentGroup = Math.ceil(currentPage / pagesPerGroup);
    const startPage = (currentGroup - 1) * pagesPerGroup + 1;
    const endPage = Math.min(currentGroup * pagesPerGroup, totalPages);

    // 이전 버튼
    if (currentGroup > 1) {
        const prevButton = document.createElement('button');
        prevButton.className = 'page-button btn btn-light'; // 버튼 간격 조정을 위해 margin을 추가하지 않음
        prevButton.textContent = '이전';
        prevButton.onclick = () => {
            currentPage = (currentGroup - 2) * pagesPerGroup + 1;
            searchArticle();
            window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
        };
        paginationControls.appendChild(prevButton);
    }

    // 페이지 번호 버튼
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = 'page-button btn btn-light'; // 버튼 간격 조정을 위해 margin을 추가하지 않음
        pageButton.textContent = i;
        if (i === currentPage) {
            pageButton.classList.add('active');
        }
        pageButton.onclick = () => {
            currentPage = i;
            searchArticle();
            window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
        };
        paginationControls.appendChild(pageButton);
    }

    // 다음 버튼
    if (currentGroup < Math.ceil(totalPages / pagesPerGroup)) {
        const nextButton = document.createElement('button');
        nextButton.className = 'page-button btn btn-light'; // 버튼 간격 조정을 위해 margin을 추가하지 않음
        nextButton.textContent = '다음';
        nextButton.onclick = () => {
            currentPage = currentGroup * pagesPerGroup + 1;
            searchArticle();
            window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
        };
        paginationControls.appendChild(nextButton);
    }
}

function fetchArticlesForPage(pageNumber) {
    fetch(`/api/article/recent?page=${pageNumber}&limit=${articlesPerPage}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        displayRecentArticles(resBody["articles"]);
        updatePaginationControls(resBody["totalArticles"]);
    }).catch((error) => {
        console.log('[Error]fetchArticlesForPage():', error);
    });
}

// 초기 페이지 로드 시 첫 페이지 데이터를 가져옴
document.addEventListener('DOMContentLoaded', () => {
    fetchArticlesForPage(currentPage);
});

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

    fetch(`/api/article/search?page=${currentPage}&limit=${articlesPerPage}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        const prevSR = document.querySelectorAll('#search_result_div .card');

        if (prevSR.length > 0) {
            prevSR.forEach((prevItem) => {
                prevItem.remove();
            });
        }

        if (resBody["success"] === true) {
            displaySearchResults(resBody["articles"]);
            updatePaginationControls(resBody["totalArticles"]); // 페이지네이션 업데이트
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

searchButton.addEventListener('click', () => {
    currentPage = 1; // 검색 버튼 클릭 시 페이지 번호를 초기화
    searchArticle();
    window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
});
noDairyCheckbox.addEventListener('change', () => {
    currentPage = 1;
    searchArticle();
    window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
});
vegetarianCheckbox.addEventListener('change', () => {
    currentPage = 1;
    searchArticle();
    window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
});
veganCheckbox.addEventListener('change', () => {
    currentPage = 1;
    searchArticle();
    window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
});
nutCheckbox.addEventListener('change', () => {
    currentPage = 1;
    searchArticle();
    window.scrollTo(0, 0); // 페이지 맨 위로 즉시 이동
});

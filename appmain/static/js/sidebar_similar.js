function displaySimilarRecipes(similarRecipes) {
    const similarViewedDiv = document.querySelector('#similar_viewed');

    similarViewedDiv.innerHTML = '';

    if (similarRecipes && similarRecipes.length > 0) {
        similarRecipes.forEach(recipe => {
            const similarItemLink = document.createElement('a');
            similarItemLink.className = 'similar-item-link';
            similarItemLink.href = `/display_article/${recipe.articleNo}`;

            const similarItemDiv = document.createElement('div');
            similarItemDiv.className = 'similar-item';

            const articleElement = `
                <img src="${recipe.image}" alt="${recipe.recipeName}">
                <p>${recipe.recipeName}</p>
            `;

            similarItemDiv.innerHTML = articleElement;
            similarItemLink.appendChild(similarItemDiv);
            similarViewedDiv.appendChild(similarItemLink);
        });
    } else {
        const errorMessage = document.createElement('p');
        errorMessage.textContent = '유사한 레시피가 없습니다.';
        similarViewedDiv.appendChild(errorMessage);
    }
}

function getArticleNo() {
    const url = window.location.pathname;
    const parts = url.split('/');
    return parts[parts.length - 1];
}

function displayRecentArticles(articles) {
    const container = document.getElementById('recent_articles_div');
    container.innerHTML = '';

    if (articles && articles.length > 0) {
        articles.forEach(article => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'card mt-2';

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
                        ${article.image ? `<img src="${article.image}" alt="레시피 이미지" class="img-fluid rounded-start">` : ''}
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <p class="card-text">재료: ${article.ingredients.split(' ').join(', ')}</p>
                        </div>
                    </div>
                </div>
            `;

            cardDiv.innerHTML = articleElement;
            container.appendChild(cardDiv);
        });

        container.querySelectorAll('a[data-articleNo]').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const articleNo = this.getAttribute('data-articleNo');
                window.location.href = `/display_article/${articleNo}`;
            });
        });
    } else {
        const errorMessage = document.createElement('p');
        errorMessage.textContent = '사용자가 최근에 조회한 레시피가 없습니다.';
        container.appendChild(errorMessage);
    }
    const footerMessage = document.getElementById('footer_message');
    footerMessage.style.display = 'block';
}

function fetchSimilarRecipes() {
    const articleNo = getArticleNo();

    fetch(`/api/recommend/similar/${articleNo}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then((resBody) => {
        const similarRecipes = resBody["similar_recipes"];
        displaySimilarRecipes(similarRecipes);
    }).catch((error) => {
        console.log('[Error]fetchSimilarRecipes():', error);
    });
}

fetchSimilarRecipes();
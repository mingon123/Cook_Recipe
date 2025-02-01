document.addEventListener('DOMContentLoaded', function() {
    const recentArticlesDiv = document.querySelector('#recent_articles_div');
    const footerMessage = document.getElementById('footer_message');

    function displayRecentArticles(articles) {
        const container = document.getElementById('recent_articles_div');
        container.innerHTML = '';

        if (articles && articles.length > 0) {
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
        } else {
            const errorMessage = document.createElement('p');
            errorMessage.textContent = '사용자가 최근에 조회한 레시피가 없습니다.';
            container.appendChild(errorMessage);
        }
    }

    function fetchRecentArticles() {
        fetch('/api/recommend1', {
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
            const recommendedRecipes = resBody["recommended_recipes"];
            displayRecentArticles(recommendedRecipes);
            footerMessage.style.display = 'block';
        }).catch((error) => {
            console.log('[Error]fetchRecentArticles():', error);
        });
    }

    fetchRecentArticles();
    fetchRecentViewedArticles();
});
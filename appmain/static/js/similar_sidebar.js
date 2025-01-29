document.addEventListener('DOMContentLoaded', function() {
    const similarViewedDiv = document.querySelector('#similar_viewed');

    function displaySimilarRecipes(similarRecipes) {
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

    function fetchSimilarRecipes() {
        const articleNo = getArticleNo();

        fetch(`/api/article/similar/${articleNo}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then((response) => {
            return response.json();
        }).then((resBody) => {
            const similarRecipes = resBody["similar_recipes"];
            displaySimilarRecipes(similarRecipes);
        }).catch((error) => {
            console.log('[Error]fetchSimilarRecipes():', error);
        });
    }

    fetchSimilarRecipes();
});
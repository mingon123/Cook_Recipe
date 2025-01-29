function displayRecentViewedArticles(articles) {
    const container = document.getElementById('recent_viewed');
    container.innerHTML = '';

    articles.forEach(article => {
        const recentItemLink = document.createElement('a');
        recentItemLink.className = 'recent-item-link';
        recentItemLink.href = `/display_article/${article.articleNo}`;

        const recentItemDiv = document.createElement('div');
        recentItemDiv.className = 'recent-item';

        const articleElement = `
            <img src="${article.image}" alt="${article.recipeName}">
            <p>${article.recipeName}</p>
        `;

        recentItemDiv.innerHTML = articleElement;
        recentItemLink.appendChild(recentItemDiv);
        container.appendChild(recentItemLink);
    });
}

    function fetchRecentViewedArticles() {
        fetch('/api/article/recent_user_visits', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then((response) => {
            return response.json();
        }).then((resBody) => {
            if (resBody.success) {
                displayRecentViewedArticles(resBody["articles"]);
            } else {
                displayRecentViewedArticles([]);
            }
        }).catch((error) => {
            console.log('[Error]fetchRecentViewedArticles():', error);
            displayRecentViewedArticles([]);
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


window.addEventListener('load', () => {
    getRecentArticles();
    fetchRecentViewedArticles();
});


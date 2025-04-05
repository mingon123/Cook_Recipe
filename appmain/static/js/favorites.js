const favoritesList = document.getElementById('favorites_list');

function displayFavorites(favorites) {
    favoritesList.innerHTML = '';
    favorites.forEach(favorite => {
        const colDiv = document.createElement('div');
        colDiv.style.flex = "0 0 20rem";
        colDiv.style.margin = "5px";

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card mb-4';

        const img = document.createElement('img');
        img.className = 'card-img-top';
        img.src = favorite.image;
        img.alt = favorite.recipeName;
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
            window.location.href = `/display_article/${favorite.articleNo}`;
        });

        const favoriteIcon = document.createElement('i');
        favoriteIcon.className = 'fas fa-star favorite-icon';
        favoriteIcon.classList.add(favorite.isFavorite ? 'favorite-active' : '');
        favoriteIcon.addEventListener('click', (event) => {
            event.stopPropagation();
            toggleFavorite(favorite.articleNo, favoriteIcon);
        });

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const cardTitle = document.createElement('h5');
        cardTitle.className = 'card-title';
        cardTitle.style.cursor = 'pointer';
        cardTitle.textContent = favorite.recipeName;
        cardTitle.addEventListener('click', () => {
            window.location.href = `/display_article/${favorite.articleNo}`;
        });

        cardBody.appendChild(cardTitle);
        cardDiv.appendChild(img);
        cardDiv.appendChild(favoriteIcon);
        cardDiv.appendChild(cardBody);
        colDiv.appendChild(cardDiv);
        favoritesList.appendChild(colDiv);
    });
}

function fetchFavorites() {
    fetch('/api/favorite', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayFavorites(data.favorites);
        } else {
            console.error('Failed to fetch favorites:', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function toggleFavorite(articleNo, icon) {
    const isRemoving = icon.classList.contains('favorite-active');

    fetch(`/api/favorite/${articleNo}`, {
        method: isRemoving ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: isRemoving ? null : JSON.stringify({ article_no: articleNo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            icon.classList.toggle('favorite-active');
        } else {
            console.error('Failed to toggle favorite:', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

fetchFavorites();

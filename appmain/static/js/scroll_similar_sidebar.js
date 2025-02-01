document.addEventListener('DOMContentLoaded', function() {
    const similarRecipesContainer = document.querySelector('.similar-recipes-container');
    const similarRecipes = document.querySelector('.similar-recipes');

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const offsetHeight = document.documentElement.scrollHeight;
        const innerHeight = window.innerHeight;
        const sidebarHeight = similarRecipes.offsetHeight;

        if (scrollTop + innerHeight >= offsetHeight - sidebarHeight - 100) {
            similarRecipesContainer.style.position = 'absolute';
            similarRecipesContainer.style.top = `${offsetHeight - sidebarHeight}px`;
        } else {
            similarRecipesContainer.style.position = 'fixed';
            similarRecipesContainer.style.top = '100px';
            similarRecipesContainer.style.left = '20px';
            similarRecipesContainer.style.bottom = '100px';
        }
    });
});

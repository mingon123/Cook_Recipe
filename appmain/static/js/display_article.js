sessionStorage.setItem("user_id", "{{ user_id }}");

function getArticleNo() {
    const location = window.location.href;
    const url = new URL(location);
    const articleNo = url.pathname.split('/')[2];

    return articleNo;
}

function getUserId() {
    return sessionStorage.getItem("user_id");
}

function displayArticle(recipeName, ingredients, cookingMethod, cuisineType, calories, carbohydrates, protein, fat, sodium, att_file_no_mk, rcp_na_tip,
                        manual1, manual_img1, manual2, manual_img2, manual3, manual_img3, manual4, manual_img4, manual5, manual_img5, manual6, manual_img6) {
    const titleSection = document.querySelector('#article_title_div');
    const descSection = document.querySelector('#article_desc_div');
    const imageFigure = document.querySelector('#article_image_fig');
    const nutritionSection = document.querySelector('#nutrition_info_div');
    const cookingSequenceSection = document.querySelector('#cooking_sequence_div');
    const tipsSection = document.querySelector('#tips_div');

    let titleDiv = document.createElement('div');
    titleDiv.className = 'col-7';
    titleDiv.id = 'article_title';
    let title = `[${cuisineType}] ${recipeName}`;
    titleDiv.appendChild(document.createTextNode(title));
    titleSection.appendChild(titleDiv);

    if (att_file_no_mk && att_file_no_mk.length > 0) {
        let image = document.createElement('img');
        image.src = att_file_no_mk;
        image.className = 'figure-img img-fluid rounded';
        imageFigure.appendChild(image);
    }

    let descDiv = document.createElement('div');
    descDiv.className = 'col-9';
    descDiv.id = 'article_desc';
    descDiv.innerHTML = `
        <p><strong style="font-size: 20px;">재료</strong><br> ${ingredients}</p>
        <br>
        <p><strong style="font-size: 18px;">조리 방법:</strong> ${cookingMethod}</p>
    `;
    descSection.appendChild(descDiv);

    let nutritionDiv = document.createElement('div');
    nutritionDiv.className = 'col-9';
    nutritionDiv.id = 'nutrition_info';
    nutritionDiv.innerHTML = `
        <p><strong style="font-size: 18px;">영양 정보 (1회 제공량당)</strong></p>
        <p>열량: ${calories}kcal</p>
        <p>탄수화물: ${carbohydrates}g</p>
        <p>단백질: ${protein}g</p>
        <p>지방: ${fat}g</p>
        <p>나트륨: ${sodium}mg</p>
    `;
    nutritionSection.appendChild(nutritionDiv);

    if (rcp_na_tip && rcp_na_tip.trim().length > 0) {
        let tipsDiv = document.createElement('div');
        tipsDiv.className = 'col-9';
        tipsDiv.id = 'tips';
        let tipsTitle = document.createElement('p');
        tipsTitle.innerHTML = '<strong style="font-size: 18px;">요리 TIP</strong>';
        let tipsContent = document.createElement('p');
        tipsContent.innerHTML = rcp_na_tip;
        tipsDiv.appendChild(tipsTitle);
        tipsDiv.appendChild(tipsContent);
        tipsSection.appendChild(tipsDiv);
    }

    if (manual1 && manual1.trim().length > 0) {
        let cookingSequenceDiv = document.createElement('div');
        cookingSequenceDiv.className = 'col-9 cooking-step';
        cookingSequenceDiv.id = 'cooking_sequence';

        let manuals = [manual1, manual2, manual3, manual4, manual5, manual6];
        let images = [manual_img1, manual_img2, manual_img3, manual_img4, manual_img5, manual_img6];

        for (let i = 0; i < manuals.length; i++) {
            if (manuals[i] && manuals[i].trim().length > 0) {
                let sequenceHtml = '';
                if (i === 0) {
                    sequenceHtml += '<br><p><strong style="font-size: 20px;">조리 순서</strong></p>';
                }
                if (manuals[i].trim().match(/^\d+\./)) {
                    sequenceHtml += '<br>';
                }
                sequenceHtml += `${manuals[i]}<br>`;
                cookingSequenceDiv.innerHTML += sequenceHtml;

                if (images[i] && images[i].trim().length > 0) {
                    let image = document.createElement('img');
                    image.src = images[i];
                    image.className = 'figure-img img-fluid rounded';
                    cookingSequenceDiv.appendChild(image);
                }
                cookingSequenceDiv.innerHTML += '<br>';
            }
        }

        cookingSequenceSection.appendChild(cookingSequenceDiv);
    }
}

function getArticle() {
    articleNo = getArticleNo();
    const user_id = getUserId();

    let formData = new FormData();
    formData.append("articleNo", articleNo);
    formData.append("user_id", user_id);

    fetch('/api/article/display', {
        method: 'POST',
        body: formData
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        let article = resBody["article"];
        displayArticle(article["recipeName"], article["ingredients"], article["cookingMethod"], article["cuisineType"],
            article["calories"], article["carbohydrates"], article["protein"], article["fat"], article["sodium"],
            article["att_file_no_mk"], article["rcp_na_tip"], article["manual1"], article["manual_img1"],article["manual2"], article["manual_img2"],
            article["manual3"], article["manual_img3"], article["manual4"], article["manual_img4"],
            article["manual5"], article["manual_img5"], article["manual6"], article["manual_img6"]);
    }).catch((error) => {
        console.error('Error in getArticle():', error);
    });
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
        if (resBody.success) {
            displaySimilarRecipes(resBody.similar_recipes);
        } else {
            console.log('유사한 레시피를 찾을 수 없습니다.');
        }
    }).catch((error) => {
        console.log('[Error]fetchSimilarRecipes():', error);
    });
}

window.addEventListener('load', () => {
    getArticle();s
    fetchSimilarRecipes();
});
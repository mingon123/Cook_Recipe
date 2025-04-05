const signup = document.querySelector("#signup_link");
const signin = document.querySelector("#signin_link");
const signout = document.querySelector("#signout_link");
const myinfo = document.querySelector("#myinfo_link");
const favorites = document.querySelector("#favorites_link");
const recommend1Link = document.querySelector("#recommend1_link");
const recommend2Link = document.querySelector("#recommend2_link");
const recommend3Link = document.querySelector("#recommend3_link");
const recommendLink = document.querySelector("#recommend_link");
//const createArticleLink = document.querySelector("#create_article_link");

function showAndHideNavbarMenu() {
    let authtoken = window.sessionStorage.getItem("authtoken");

    if(authtoken){
        signup.style.display = "none";
        signin.style.display = "none";
    }
    else{
        signout.style.display = "none";
        myinfo.style.display = "none";
        favorites.style.display = "none";
//        recommend1Link.style.display = "none";
//        recommend2Link.style.display = "none";
//        recommend3Link.style.display = "none";
        recommendLink.style.display = "none";

//        createArticleLink.style.display = "none";
    }
}

window.addEventListener("load", showAndHideNavbarMenu);

function signOutHandler() {
    window.sessionStorage.removeItem("authtoken");
    window.sessionStorage.removeItem("username");

    let url = '/home';
    window.location.replace(url);
}

signout.addEventListener("click", signOutHandler);

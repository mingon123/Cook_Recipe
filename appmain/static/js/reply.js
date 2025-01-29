// 댓글 관련 HTML 요소 변수
const replyInput = document.querySelector('#reply_input');
const leaveReplyDiv = document.querySelector('#leave_reply_div');
const leaveReplyButton = document.querySelector('#leave_reply_button');
const displayReplyDiv = document.querySelector('#display_reply_div');
const moreRepliesButton = document.querySelector('#more_replies_button');

//댓글 입력 유효성 검사
function checkReplyInput() {
    return replyInput.value.length > 0;
}


//댓글 달기
function onLeaveReplyHandler() {
    const articleNo = getArticleNo();
    let isReplyInputValid = checkReplyInput();

    if(isReplyInputValid === true){
        let headerData = new Headers();
        let authToken = sessionStorage.getItem("authtoken");
        if(authToken){
            headerData.set("authtoken", authToken);
        }

        let formData = new FormData();

        formData.set("articleNo", articleNo);
        formData.set("reply", replyInput.value);

        fetch('/api/reply/leave', {
            method: 'POST',
            headers: headerData,
            body: formData
        }).then((response) => {
            return response.json();
        }).then((resBody) => {
            console.log(resBody)

            let replyRow = document.createElement('div');
            replyRow.className = 'row justify-content-center mt-2';
            replyRow.id = `reply_row-${resBody["replyNo"]}`

            replyContent = `
                <div class="col-1">
                </div>
                <div class="col-6">
                    <div class="row">
                        <div class="col-2">
                            ${resBody["author"]}
                        </div>
                        <div class="col-7">
                            ${resBody["desc"]}
                        </div>
                    </div>
                </div>
                <div class="col-2" class="delete_reply_button_div">
                    <button type="button" class="btn btn-secondary btn-sm" data-replyno="${resBody["replyNo"]}">삭제</button>
                </div>`;

            replyRow.innerHTML = replyContent;

            let deleteButton = replyRow.querySelector('button');
            deleteButton.addEventListener('click', onDeleteReplyHandler);

            displayReplyDiv.insertBefore(replyRow, displayReplyDiv.firstChild);

            replyInput.value = '';
            baseIndex = baseIndex + 1;
        }).catch((error) => {
            console.log('[Error]create_article.onSubmitHandler:', error);
        });
    }
}

//댓글 삭제
function onDeleteReplyHandler(event) {
    const replyNo = event.currentTarget.dataset.replyno;

    let headerData = new Headers();
    const authToken = sessionStorage.getItem("authtoken");
    if(authToken){
        headerData.set("authtoken", authToken);
    }

    let formData = new FormData();

    formData.set("replyNo", replyNo);

    fetch('/api/reply/delete', {
        method: 'POST',
        headers: headerData,
        body: formData
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        if(resBody["success"] === true){
            console.log('onDeleteReplyHandler():', replyNo);

            const targetReplyRowId = `#reply_row-${replyNo}`;
            const targetReplyRow = document.querySelector(targetReplyRowId);
            targetReplyRow.remove();
            baseIndex = baseIndex - 1;
        }
    }).catch((error) => {
        console.log('[Error]onDeleteReplyHandler():', error);
    });
}


//댓글 표시
function displayReply() {
    const authToken = sessionStorage.getItem("authtoken");
    if(!authToken){
        leaveReplyDiv.hidden = true;
    }
    const articleNo = getArticleNo();

    let formData = new FormData();

    formData.set("articleNo", articleNo);
    formData.set("baseIndex", baseIndex);
    formData.set("numReplyRead", numReplyRead);

    fetch('/api/reply/get', {
        method: 'POST',
        body: formData
    }).then((response) => {
        return response.json();
    }).then((resBody) => {
        console.log(resBody);

        const replies = resBody["replies"];

        replies.forEach((reply) => {
            let replyRow = document.createElement('div');
            replyRow.className = 'row justify-content-center mt-2';
            replyRow.id = `reply_row-${reply["replyNo"]}`

            replyContent = `
                <div class="col-1">
                </div>
                <div class="col-6">
                    <div class="row">
                        <div class="col-2">
                            ${reply["author"]}
                        </div>
                        <div class="col-7">
                            ${reply["desc"]}
                        </div>
                    </div>
                </div>
                <div class="col-2" class="delete_reply_button_div">
                    <button type="button" class="btn btn-secondary btn-sm" data-replyno="${reply["replyNo"]}">삭제</button>
                </div>`;

            replyRow.innerHTML = replyContent;

            let deleteButton = replyRow.querySelector('button');

            if(!authToken){
                deleteButton.hidden = true;
            }
            else{
                username = sessionStorage.getItem("username");
                author = reply["author"]

                if(username != author){
                    deleteButton.hidden = true;
                }
                else{
                    deleteButton.addEventListener('click', onDeleteReplyHandler);
                }
            }

            displayReplyDiv.appendChild(replyRow);
        });

        if(resBody["moreReplies"] === false){
            moreRepliesButton.hidden = true;
        }

        baseIndex = baseIndex + numReplyRead;
    }).catch((error) => {
        console.log("[Error]getReply():", error);
    });
}

window.addEventListener('load', () => {
    displayReply();
    leaveReplyButton.addEventListener('click', onLeaveReplyHandler);
    moreRepliesButton.addEventListener('click', displayReply);
});


// 댓글 기능 관련 추가 변수
let baseIndex = 0;
const numReplyRead = 3;

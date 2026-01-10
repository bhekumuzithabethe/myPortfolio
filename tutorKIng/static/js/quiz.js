const url = window.location.href
console.log('quiz.js running')
$.ajax({
    type: 'GET',
    url:`${url}data`,
    success : function (response) {
        console.log(response)
    }
})
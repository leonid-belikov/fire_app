'use strict';

const userForm = document.querySelector('#user_form');

userForm.onsubmit = function (event) {
    event.preventDefault();
    let url = 'http://127.0.0.1:8000/landing/add_user/';
    let data = new FormData(event.target);

    fetch(url, {
        method: 'post',
        body: data
    }).then(function(response) {
        response.json().then(function(json) {
            let usersTableBody = document.querySelector('#usersTable tbody');
            usersTableBody.innerHTML = '';
            for (let user_id in json) {
                let user_td = document.createElement('td');
                let email_td = document.createElement('td');
                let row = document.createElement('tr');
                user_td.innerText = json[user_id].name;
                email_td.innerText = json[user_id].email;
                row.appendChild(user_td);
                row.appendChild(email_td);
                usersTableBody.appendChild(row);
            }
        });
    });
};

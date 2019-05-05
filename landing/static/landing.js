'use strict';

const userForm = document.querySelector('#user_form');
const self = this;

userForm.onsubmit = function (event) {
    event.preventDefault();
    let url = event.target.action;
    let data = new FormData(event.target);

    fetch(url, {
        method: 'post',
        body: data
    }).then(function(response) {
        response.json().then(function(json) {
            let usersTableBody = document.querySelector('#usersTable tbody');
            usersTableBody.innerHTML = '';
            for (let i=0; i<json.length; i++) {
                let row = self.addRowToUserTable(json[i]);
                usersTableBody.appendChild(row);
            }
        });
    });
};

// data - объект, содержащий ключи: id, name, email
function addRowToUserTable(data) {
    let user_td = document.createElement('td');
    let email_td = document.createElement('td');
    let row = document.createElement('tr');
    user_td.innerText = data['name'];
    email_td.innerText = data['email'];
    row.setAttribute('user_id', data['id'].toString());
    row.appendChild(user_td);
    row.appendChild(email_td);

    return row;
}

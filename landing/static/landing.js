'use strict';


const self = this;


const commentArea = document.querySelector('#id_comment');
commentArea.setAttribute('placeholder', 'Заполнять не обязательно');


setTabHandlers();


function setTabHandlers() {
    let MMForm = document.querySelector('#mm_form');
    let dateBox = document.querySelector('.date_wrapper');

    if (MMForm) {
        MMForm.onsubmit = function (event) {
            event.preventDefault();
            let target = event.target;
            let url = target.action;
            let data = new FormData(target);
            let isIncome = document.querySelector('#direction').checked;
            data.append('direction', isIncome ? 'income' : 'cost');

            fetch(url, {
                method: 'post',
                body: data
            }).then(function (response) {
                response.json().then(function (json) {
                    self.reloadMMTable(json);
                });
            });
        };
    }

    if (dateBox) {
        dateBox.onclick = function (event) {
            let target = event.target;
            if (target.className.includes('date_item')) {
                let url = '/landing/filter_by_date/';
                let data = new FormData;
                data.append('date', target.innerText);
                let headers = {
                    'X-CSRFToken': self.getCSRFToken()
                };
                fetch(url, {
                    method: 'post',
                    headers: headers,
                    body: data
                }).then(function (response) {
                    response.json().then(function (json) {
                        self.reloadMMTable(json);
                    });
                });
            }
        };
    }
}


function reloadMMTable(json) {
    if ('Error' in json) {
        let mmTable = document.querySelector('#mm_table');
        mmTable.innerText = 'Data error: ' + json.Error;
    } else {
        let mmTableBody = document.querySelector('#mm_table tbody');
        mmTableBody.innerHTML = '';
        for (let i = 0; i < json['items'].length; i++) {
            let row = self.addRowToMMTable(json['items'][i]);
            mmTableBody.appendChild(row);
        }
        if (json['total_amount']) {
            let totalAmountSpan = document.querySelector('#total_amount');
            totalAmountSpan.innerText = json['total_amount'];
        }
    }
}


function addRowToMMTable(data) {
// data - объект, содержащий ключи: id, date, amount, purpose, tag, comment

    let row = document.createElement('tr');
    let columns = ['date', 'amount', 'purpose', 'tag', 'comment'];

    for (let i=0; i<columns.length; i++) {
        let key = columns[i];
        let td = document.createElement('td');
        if (key in data) {
            td.innerText = key === 'tag' ? '#' : '';
            td.innerText += data[key];
        }
        td.className = key;
        if (key === 'comment') {
            td.setAttribute('title', data[key]);
        }
        row.appendChild(td);
    }

    row.setAttribute('mm_id', data['id'].toString());
    if (data['direction'] === 'income') {
        row.className = 'income_item';
    }

    return row;
}


function getCSRFToken() {
    let cookies = document.cookie;
    if (!cookies) {
        return null;
    }
    if (cookies.includes('csrftoken')) {
        let begin_index = cookies.indexOf('csrftoken');
        return cookies.slice(begin_index+10, begin_index+74);
    }
}


const tabTitlesBox = document.querySelector('.tabs_header');

tabTitlesBox.onclick = function (event) {
    let target = event.target;
    if (target.className.includes('tab_title')) {
        let currentTabTitle = document.querySelector('.tab_title.current');
        let url = '/landing/tab/';
        let data = new FormData;

        //Перебросим класс заголовка текущей вкладки
        currentTabTitle.classList.remove('current');
        target.classList.add('current');

        //Обновим контент вкладки
        data.append('template', target.getAttribute('template'));
        let headers = {
            'X-CSRFToken': self.getCSRFToken()
        };
        fetch(url, {
            method: 'post',
            headers: headers,
            body: data
        }).then(function(response) {
            response.text().then(function(text) {
                let tabContentBox = document.querySelector('.tab_content');
                tabContentBox.innerHTML = text;
                setTabHandlers();
            });
        });
    }
};
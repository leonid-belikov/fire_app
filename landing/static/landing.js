'use strict';


const self = this;


setTabHandlers();


function setTabHandlers() {
    let MMForm = document.querySelector('#mm_form');
    let MMPlanForm = document.querySelector('#mm_plan_form');
    let dateBox = document.querySelector('.date_wrapper');
    let dateSelectForm = document.querySelector('#select_date_form');

    // вынести куда-то в другое место, т.к. это не относится к данной функции по смыслу
    let commentArea = document.querySelector('#id_comment');
    if (commentArea) {
        commentArea.setAttribute('placeholder', 'Заполнять не обязательно');
    }


    let formSender = function (form, checkbox_selector, callback) {
        form.onsubmit = function (event) {
            event.preventDefault();
            let target = event.target;
            let url = target.action;
            let data = new FormData(target);
            let isIncome = document.querySelector(checkbox_selector).checked;
            data.append('direction', isIncome ? 'income' : 'cost');

            fetch(url, {
                method: 'post',
                body: data
            }).then(function (response) {
                callback(response);
            });
        };
    };

    let MMFormCallback = function (response) {
        response.text().then(function (text) {
            let mmTableWrapper = document.querySelector('#mm_table_wrap');
            mmTableWrapper.innerHTML = text;
            reloadTotalAmountAndDates();
        });
    };

    let MMPlanFormCallback = function (response) {
        response.text().then(function (text) {
            let mmPlanTable = document.querySelector('.mm_plan_tables');
            mmPlanTable.innerHTML = text;
            // Тут добавить обновление запланированной суммы на странице
        });
    };

    let reloadTotalAmountAndDates = function () {
        let url = '/landing/reload_total_amount/';
        let headers = {
            'X-CSRFToken': self.getCSRFToken()
        };
        fetch(url, {
            method: 'post',
            headers: headers
        }).then(function (response) {
            response.json().then(function (json) {
                if (json['total_amount']) {
                    let totalAmountSpan = document.querySelector('#total_amount');
                    totalAmountSpan.innerText = json['total_amount'];
                }
                if (json['dates']) {
                    let dates = json['dates'];
                    let datesBox = document.querySelector('.date_wrapper');

                    datesBox.innerHTML = '';
                    for (let i=0; i<dates.length; i++) {
                        let dateBox = document.createElement('div');
                        dateBox.className = 'date_item';
                        dateBox.innerText = dates[i]['day'];
                        dateBox.setAttribute('date', dates[i]['date_str']);
                        datesBox.appendChild(dateBox);
                    }
                }
            })
        })
    };

    if (MMForm) {
        formSender(MMForm, '#direction', MMFormCallback);
    }

    if (MMPlanForm) {
        formSender(MMPlanForm, '#plan_direction', MMPlanFormCallback);
    }

    if (dateBox) {
        dateBox.onclick = function (event) {
            let target = event.target;
            if (target.className.includes('date_item')) {
                let url = '/landing/filter_by_date/';
                let data = new FormData;
                data.append('date', target.getAttribute('date'));
                let headers = {
                    'X-CSRFToken': self.getCSRFToken()
                };
                fetch(url, {
                    method: 'post',
                    headers: headers,
                    body: data
                }).then(function (response) {
                    response.text().then(function (text) {
                        let mmTableBody = document.querySelector('#mm_table_wrap');
                        mmTableBody.innerHTML = text;
                    });
                });
            }
        };
    }

    dateSelectForm.onsubmit = function (event) {
        event.preventDefault();
        let currentTabTitle = document.querySelector('.tab_title.current');
        let target = event.target;
        let url = target.action;
        let data = new FormData(target);

        data.append('template', currentTabTitle.getAttribute('template'));

        fetch(url, {
            method: 'post',
            body: data
        }).then(function (response) {
            response.text().then(function(text) {
                let tabContentBox = document.querySelector('.tab_content');
                tabContentBox.innerHTML = text;
                setTabHandlers();
            });
        });

    }
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

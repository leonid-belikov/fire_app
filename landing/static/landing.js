'use strict';


let currentMonth;
let currentYear;


setTabHandlers();


function setTabHandlers() {
    let MMForm = document.querySelector('#mm_form');
    let MMPlanForm = document.querySelector('#mm_plan_form');
    let dateBox = document.querySelector('.date_wrapper');
    let dateSelectForm = document.querySelector('#select_date_form');
    let MMTable = document.querySelector('#mm_table');

    // TODO: вынести куда-то в другое место, т.к. это не относится к данной функции
    //  по смыслу. Переделать в цикл.
    let commentArea = document.querySelector('#id_comment');
    let amountArea = document.querySelector('#id_amount');
    let purposeArea = document.querySelector('#id_purpose');
    let categoryArea = document.querySelector('#id_category');
    if (commentArea) {
        commentArea.setAttribute('placeholder', 'Комментарий (заполнять не обязательно)');
    }
    if (amountArea) {
        amountArea.setAttribute('placeholder', 'Сумма');
    }
    if (purposeArea) {
        purposeArea.setAttribute('placeholder', 'Назначение');
    }
    if (categoryArea) {
        categoryArea.setAttribute('placeholder', 'Категория');
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
            'X-CSRFToken': getCSRFToken()
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
                setTabHandlers();
            })
        })
    };

    // Добавить новое фактическое движение средств
    if (MMForm) {
        formSender(MMForm, '#direction', MMFormCallback);
    }

    // Добавить новое плановое движение средств
    if (MMPlanForm) {
        formSender(MMPlanForm, '#plan_direction', MMPlanFormCallback);
    }

    // Выбор даты в фильтре по датам
    if (dateBox) {
        dateBox.onclick = function (event) {
            let target = event.target;
            if (target.className.includes('date_item')) {
                let url = '/landing/filter_by_date/';
                let data = new FormData;
                data.append('date', target.getAttribute('date'));
                let headers = {
                    'X-CSRFToken': getCSRFToken()
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

    // Выбор месяца и года в шапке
    dateSelectForm.onsubmit = function (event) {
        event.preventDefault();
        let currentTabTitle = document.querySelector('.tab_title.current');
        let target = event.target;
        let url = target.action;
        let data = new FormData(target);

        currentMonth = data.get('month');
        currentYear = data.get('year');

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
    };

    // Клик по таблице с фактическими движениями средств, редактор по месту
    if (MMTable) {
        MMTable.onclick = function (event) {
            let targetRow = event.target;
            let focusName = '';
            while (true) {
                if (!targetRow) {
                    break;
                }
                if (targetRow.className.includes('tab_content')) {
                    targetRow = null;
                    break;
                }
                if (targetRow.className.includes('mm_data')) {
                    focusName = targetRow.getAttribute('mm_data_name');
                }
                if (targetRow.className.includes('mm_row')) {
                    break;
                } else {
                    targetRow = targetRow.parentElement;
                }
            }
            if (targetRow) {
                // удалим уже открытый редактор, если он есть
                let activeEditor = MMTable.querySelector('.mm_editor');
                if (activeEditor)
                    activeEditor.remove();
                // соберем данные из записи
                let mmData = {};
                let childList = targetRow.children;
                mmData['id'] = targetRow.getAttribute('mm_id');
                for (let i=0; i<childList.length; i++) {
                    let child = childList[i];
                    if (child.className.includes('amount')) {
                        mmData['amount'] = child.innerText;
                    }
                    if (child.className.includes('purpose_wrap')) {
                        for (let i=0; i<child.children.length; i++) {
                            let elem = child.children[i];
                            if (elem.className.includes('purpose')) {
                                mmData['purpose'] = elem.innerText;
                            }
                            if (elem.className.includes('category')) {
                                mmData['category'] = elem.innerText;
                            }
                        }
                    }
                    if (child.className.includes('comment')) {
                        mmData['comment'] = child.innerText;
                    }
                }
                // сгенерируем окно с формой
                let MMRowEditor = document.querySelector('.mm_editor').cloneNode(true);
                let amountBox = MMRowEditor.querySelector('.editor_amount');
                let purposeBox = MMRowEditor.querySelector('.editor_purpose');
                let categoryBox = MMRowEditor.querySelector('.editor_category');
                let commentBox = MMRowEditor.querySelector('.editor_comment');
                let td = MMTable.querySelector('td.editor');
                amountBox.setAttribute('value', mmData['amount']);
                purposeBox.setAttribute('value', mmData['purpose']);
                categoryBox.setAttribute('value', mmData['category']);
                commentBox.innerText = mmData['comment'];
                MMRowEditor.style.top = targetRow.offsetTop + 'px';
                MMRowEditor.style.left = targetRow.offsetLeft + 'px';
                MMRowEditor.style.display = 'block';
                td.appendChild(MMRowEditor);
                // установим фокус на поле, по которому был клик
                if (focusName) {
                    let focusClassSelector = '.editor_' + focusName;
                    MMRowEditor.querySelector(focusClassSelector).focus();
                }
                // обработаем клик по кнопке "V" - проверим, были ли изменения:
                // если да - обновим строку, если нет - просто закроем редактор
                let MMRowForm = document.querySelector('#mm_row_form');
                MMRowForm.onsubmit = function (event) {
                    event.preventDefault();
                    let target = event.target;
                    let url = target.action;
                    let formData = new FormData(target);
                    let data = new FormData();
                    let dataIsNotEmpty = false;
                    for (let [name, value] of formData) {
                        if (mmData.hasOwnProperty(name) && mmData[name] !== value) {
                            data.append(name, value);
                            dataIsNotEmpty = true;
                        }
                    }
                    if (dataIsNotEmpty) {
                        let headers = {
                            'X-CSRFToken': getCSRFToken()
                        };
                        data.append('id', mmData['id']);

                        fetch(url, {
                            method: 'post',
                            headers: headers,
                            body: data
                        }).then(function (response) {
                            response.text().then(function(text) {
                                targetRow.innerHTML = text;
                                MMRowEditor.remove();
                            });
                        });

                    } else {
                        MMRowEditor.remove();
                    }
                };

                // обработаем клик по кнопке "Х" - закроем редактор
                let closeButton = document.querySelector('#mm_row_form button.close');
                closeButton.onclick = function (event) {
                    MMRowEditor.remove();
                };

                // обработаем клик по кнопке "Удалить"
                let deleteButton = document.querySelector('#mm_row_form button.delete');
                deleteButton.onclick = function (event) {
                    let url = '/landing/delete_mm_row/';
                    let data = new FormData;
                    data.append('id', mmData['id']);
                    let headers = {
                        'X-CSRFToken': getCSRFToken()
                    };
                    fetch(url, {
                        method: 'post',
                        headers: headers,
                        body: data
                    }).then(function (response) {
                        response.text().then(function (text) {
                            let mmTableBody = document.querySelector('#mm_table_wrap');
                            mmTableBody.innerHTML = text;
                            reloadTotalAmountAndDates();
                        });
                    });
                }
            }
        }
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

// Клик по заголовку вкладки
tabTitlesBox.onclick = function (event) {
    let target = event.target;
    if (target.className.includes('tab_title')) {
        let currentTabTitle = document.querySelector('.tab_title.current');
        let url = '/landing/tab/';
        let data = new FormData;

        // Перебросим класс заголовка текущей вкладки
        currentTabTitle.classList.remove('current');
        target.classList.add('current');

        // Обновим контент вкладки
        data.append('template', target.getAttribute('template'));
        if (currentMonth && currentYear) {
            data.append('month', currentMonth);
            data.append('year', currentYear);
        }
        let headers = {
            'X-CSRFToken': getCSRFToken()
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

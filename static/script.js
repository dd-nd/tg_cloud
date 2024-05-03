function fillData(api_name, obj) {
    let xhr = new XMLHttpRequest();
    
    xhr.open('POST', api_name, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            let data = JSON.parse(xhr.responseText);
            let dropdown = document.getElementById(obj);
            
            data.forEach(function(item) {
                let option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                dropdown.appendChild(option);
            });
        } else {
            console.error('Произошла ошибка при получении данных:', xhr.statusText);
        }
    };
    
    xhr.onerror = function() {
        console.error('Произошла ошибка при получении данных:', xhr.statusText);
    };
    
    xhr.send();
}
document.addEventListener('DOMContentLoaded', function() {
    const dictionary = [
        {'api_name':'/getTypesData', 'obj':'dropdown-type'},
        {'api_name':'/getGenresData', 'obj':'dropdown-genre'},
        {'api_name':'/getStatusesData', 'obj':'dropdown-status'}
    ];
    
    for (let item of dictionary) {
        fillData(item.api_name, item.obj);
    }
});

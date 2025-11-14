// inspection results
 function fill_results(inspection_results) {
    const dimensions = Object.keys(inspection_results)
    for (let i = 0; i != dimensions.length; i++) {
        var row_objects = $('#' + dimensions[i] + ' td');

        var measured = inspection_results[dimensions[i]];
        row_objects[0].textContent = measured;

        var nominal = row_objects[1].textContent;

        var delta = measured - nominal;
        row_objects[2].textContent = delta.toFixed(2);

        var tolerance_upper, tolerance_lower
        [tolerance_upper, tolerance_lower] = row_objects[3].textContent.split('/');

        if (delta < tolerance_lower || delta > tolerance_upper) {
            row_objects[4].textContent = 'Fail';
            row_objects[4].style.background = 'red';
        } else {
            row_objects[4].style.background = 'green';
            row_objects[4].textContent = 'Pass';
        };
    }
 };


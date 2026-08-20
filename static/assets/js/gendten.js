
    $(document).ready(function () {
        $("#id_noofequipments").change(function () {
            if ($(this).val() === '') {
                $('#select-test-equipment1').hide();
                $('#select-test-equipment2').hide();
                $('#select-test-equipment3').hide();
                $('#select-test-equipment4').hide();
            } else if ($(this).val() === '1' ) {
                $('#select-test-equipment1').show();
                $('#select-test-equipment2').hide();
                $('#select-test-equipment3').hide();
                $('#select-test-equipment4').hide();
            }else if ($(this).val() === '2' ) {
                $('#select-test-equipment1').show();
                $('#select-test-equipment2').show();
                $('#select-test-equipment3').hide();
                $('#select-test-equipment4').hide();
            }else if ($(this).val() === '3' ) {
                $('#select-test-equipment1').show();
                $('#select-test-equipment2').show();
                $('#select-test-equipment3').show();
                $('#select-test-equipment4').hide();
            } else if ($(this).val() === '4' ) {
                $('#select-test-equipment1').show();
                $('#select-test-equipment2').show();
                $('#select-test-equipment3').show();
                $('#select-test-equipment4').show();
            }else {
                $('#select-test-equipment1').hide();
                $('#select-test-equipment2').hide();
                $('#select-test-equipment3').hide();
                $('#select-test-equipment4').hide();
            }
        });
        $("#id_noofequipments").trigger("change")
    })


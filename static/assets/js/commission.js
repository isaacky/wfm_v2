$(document).ready(function () {
$("#id_txstatus").change(function () {
        if ($(this).val() === " ") {
            $('#refubby').hide();
            $('#workshop').hide();
            $('#contractor').hide();
        } else if ($(this).val() === "refurbished") {
            $('#refubby').show();
            $('#contractor').hide();

        } else if ($(this).val() === "new") {
            $('#refubby').hide();
            $('#contractor').hide();
            $('#workshop').hide();

        } else {
            $('#refubby').hide();
            $('#contractor').hide();
            $('#workshop').hide();

        }
    });
    $("#id_txstatus").trigger("change")

    $("#id_refubby").change(function () {
        if ($(this).val() === " ") {
            $('#workshop').hide();
            $('#contractor').hide();
        } else if ($(this).val() === "kplc") {
            $('#workshop').show();
            $('#contractor').hide();

        } else if ($(this).val() === "contractor") {
            $('#contractor').hide();
            $('#workshop').hide();

        } else {
            $('#workshop').hide();
            $('#contractor').hide();


        }
    });
    $("#id_refubby").trigger("change")

})
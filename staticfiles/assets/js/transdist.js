$(document).ready(function () {

    $("#id_feeder_metered").change(function () {

        if ($(this).val() === "") {
            $('#feeder_metered').hide();
        } else if ($(this).val() === "yes") {
            $('#feeder_metered').show();
        } else if ($(this).val() === "no") {
            $('#feeder_metered').hide();
        } else {
            $('#feeder_metered').hide();
        }
    });
    $("#id_feeder_metered").trigger("change")

    $("#id_ismetered").change(function () {

        if ($(this).val() === "") {
            $('#ismetered').hide();
        } else if ($(this).val() === "yes") {
            $('#ismetered').show();
        } else if ($(this).val() === "no") {
            $('#ismetered').hide();
        } else {
            $('#ismetered').hide();
        }
    });
    $("#id_ismetered").trigger("change")


    $("#id_istherenameplate").change(function () {

        if ($(this).val() === "") {
            $('#istherenameplate').hide();
        } else if ($(this).val() === "yes") {
            $('#istherenameplate').show();
        } else if ($(this).val() === "no") {
            $('#istherenameplate').hide();
        } else {
            $('#istherenameplate').hide();
        }
    });
    $("#id_istherenameplate").trigger("change")


        $("#id_feeder_metered").change(function () {

        if ($(this).val() === "") {
            $('#feeder-metered-outgoing').hide();
        } else if ($(this).val() === "yes") {
            $('#feeder-metered-outgoing').show();
        } else if ($(this).val() === "no") {
            $('#feeder-metered-outgoing').hide();
        } else {
            $('#feeder-metered-outgoing').hide();
        }
    });
    $("#id_feeder_metered").trigger("change")


    $("#id_metered").change(function () {

        if ($(this).val() === "") {
            $('#metered-aux').hide();
        } else if ($(this).val() === "yes") {
            $('#metered-aux').show();
        } else if ($(this).val() === "no") {
            $('#metered-aux').hide();
        } else {
            $('#metered-aux').hide();
        }
    });
    $("#id_metered").trigger("change")



})



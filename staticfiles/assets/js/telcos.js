 $(document).ready(function () {

        $("#id_meteringstatus").change(function () {

            if ($(this).val() === "") {
                $('#id_faultystatus').hide();
                $('#id_tamperedstatus').hide();
                $('#id_bypassstatus').hide();

            } else if ($(this).val() === "okay") {
                $('#metering-not-okay').hide();

            } else if ($(this).val() === "faulty") {

                $('#id_faultystatus').show();
                $('#id_tamperedstatus').hide();
                $('#id_bypassstatus').hide();


            } else if ($(this).val() === "tampered") {
               $('#id_faultystatus').hide();
                $('#id_tamperedstatus').show();
                $('#id_bypassstatus').hide();

            } else if ($(this).val() === "bypassed") {
                $('#id_faultystatus').hide();
                $('#id_tamperedstatus').hide();
                $('#id_bypassstatus').show();

            } else if ($(this).val() === "nometer") {
                $('#id_faultystatus').hide();
                $('#id_tamperedstatus').hide();
                $('#id_bypassstatus').hide();
            } else {
               $('#id_faultystatus').hide();
                $('#id_tamperedstatus').hide();
                $('#id_bypassstatus').hide();
            }
        });
        $("#id_meteringstatus").trigger("change")

      $("#id_installationstatus").change(function () {
            if ($(this).val() === "") {
                $('#id_notokaystatus').hide();
            } else if ($(this).val() === "okay") {
                $('#id_notokaystatus').hide();
            } else {
                $('#id_notokaystatus').show();
            }
        });
        $("#id_installationstatus").trigger("change")
    })



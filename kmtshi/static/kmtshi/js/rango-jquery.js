$(document).ready(function() {
        // Select all
        $("#all-btn").click( function() {
            $("#" + $(this).attr('rel') + " INPUT[type='checkbox']").attr('checked', true);
            return false;
        });
        // Select none
        $("#none-btn").click( function() {
            $("#" + $(this).attr('rel') + " INPUT[type='checkbox']").attr('checked', false);
            return false;
        });
        // Invert selection
        $("#invert-btn").click( function() {
            $("#" + $(this).attr('rel') + " INPUT[type='checkbox']").each( function() {
                $(this).attr('checked', !$(this).attr('checked'));
            });
            return false;
        });


});
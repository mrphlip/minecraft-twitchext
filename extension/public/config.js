function on_new_state(data) {
    if (data) {
        $('.configured').show();
        $('.loadingpane').hide();
        $('.unconfigured').hide();

        $('.playername').text(data.world.name);
        $('.worldname').text(data.world.world);
    } else {
        $('.configured').hide();
        $('.loadingpane').hide();
        $('.unconfigured').show();
    }
}

var advancement_data;

function init() {
    $('.content').tabs();
    $('.progress').progressbar({
        max: 1,
        value: 0,
    })

    $.getJSON("advancement_data.json", (adv_data) => {
        advancement_data = adv_data;
        build_page();

        $.getJSON("sample_data.json", (sample_data) => {
            update_page(sample_data);
        })
    })
}
$(init);

function css_class(name) {
    return name.replace(/[:\/]/g, '-');
}

function build_page(data) {
    var detailpane = $('#tab-detail').empty();
    var catpane = {}
    for (var cat of advancement_data.categories) {
        var header = $('<h2>').appendTo(detailpane);
        catpane[cat.id] = $('<div>').appendTo(detailpane);
        header.attr('class', 'catheader');
        $('<span>').attr('class', 'sprite cat-' + css_class(cat.id)).appendTo(header);
        header.append(' ' + cat.name)
    }
    for (var adv of advancement_data.advancements) {
        var tile = $('<div>').appendTo(catpane[adv.category]);
        tile.attr('class', 'tile sprite ' + css_class(adv.id));
        if (adv.mode == 'all') {
            var progress = $('<div>').appendTo(tile);
            progress.attr('class', 'tileprogress');
            progress.progressbar({
                max: adv.criteria.length,
                value: false,
            });
        }
        // generate the tooltip as disabled, then add our own mouseover/leave events
        // so we can override the behaviour to allow click-to-keep-alive
        tile.tooltip({
            items: '.tile',
            content: generate_tooltip,
            disabled: true,
            position: {
                my: 'center top+5',
                at: 'center bottom',
                collision: 'fit none',
                within: '#tab-detail',
            }
        });
        tile.on('mouseover', tile_mouseover);
        tile.on('mouseleave', tile_mouseleave);
        tile.click(tile_click);
    }
}

function update_page(data) {
    var count = 0, donecount = 0, latestadv, latestdata;
    for (var adv of advancement_data.advancements) {
        count++;
        if (!data.advancements[adv.id]) {
            data.advancements[adv.id] = {done: false, criteria: {}};
        }
        var advdata = data.advancements[adv.id];
        if (advdata.done) {
            donecount++;
            if (adv.mode == 'all') {
                var lastCrit;
                for (var i in advdata.criteria)
                    if (!lastCrit || advdata.criteria[i] > lastCrit)
                        lastCrit = advdata.criteria[i];
                advdata.date = lastCrit;
            } else {
                var firstCrit;
                for (var i in advdata.criteria)
                    if (!firstCrit || advdata.criteria[i] < firstCrit)
                        firstCrit = advdata.criteria[i];
                advdata.date = firstCrit;
            }
            if (!latestadv || advdata.date > latestadv.date) {
                latestadv = adv;
                latestdata = advdata;
            }
        }

        var tile = $("#tab-detail ." + css_class(adv.id));
        if (advdata.done)
            tile.addClass('done');
        else
            tile.removeClass('done');
        tile.data('adv', adv);
        tile.data('advdata', advdata);
        if (adv.mode == 'all' && !advdata.done) {
            var critcount = 0;
            for (var crit of adv.criteria)
                if (advdata.criteria[crit.id])
                    critcount++;
            tile.find('.tileprogress').progressbar('value', critcount).show();
        } else {
            tile.find('.tileprogress').hide();
        }
    }

    $('.icon').attr('src', data.world.icon);
    $('.playername').text(data.world.name);
    $('.worldname').text(data.world.world);

    $('.progress').progressbar('option', 'max', count).progressbar('value', donecount);
    $('.progress-label').text(donecount + " / " + count);

    if (latestadv) {
        $('.latestadv-icon').attr('class', 'latestadv-icon sprite done ' + css_class(latestadv.id));
        $('.latestadv-name').text(latestadv.name);
    } else {
        $('.latestadv-icon').attr('class', 'latestadv-icon');
        $('.latestadv-name').text("None");
    }

    $('.content').show();
    $('.loadingpane').hide();
}

function generate_tooltip() {
    var tile = $(this);
    var panel = $('<div>');
    var adv = tile.data('adv'), advdata = tile.data('advdata');
    panel.attr('class', 'tooltip');
    var header = $('<h3>').appendTo(panel);
    header.attr('class', 'tipheader');
    var icon = $('<span>').attr('class', 'sprite ' + css_class(adv.id)).appendTo(header);
    if (advdata.done)
        icon.addClass('done');
    header.append(' ' + adv.name);
    $('<p>').attr('class', 'description').append(adv.description).appendTo(panel);
    var list = $('<ul>').attr('class', 'criteria').appendTo(panel);
    for (var crit of adv.criteria) {
        var li = $('<li>').text(crit.description).appendTo(list);
        if (advdata.criteria[crit.id])
            li.addClass('done');
    }
    return panel;
}

var clicked;
function tile_mouseover() {
    if (!clicked)
        $(this).tooltip('open', {type: 'dummyevent', target: this});
}
function tile_mouseleave() {
    if (!clicked)
        $(this).tooltip('close');
}
function tile_click() {
    if (clicked == this) {
        $(this).tooltip('close');
        clicked = undefined;
    } else if (clicked) {
        $(clicked).tooltip('close');
        $(this).tooltip('open', {type: 'dummyevent', target: this});
        clicked = this;
    } else {
        $(this).tooltip('open', {type: 'dummyevent', target: this});
        clicked = this;
    }
}
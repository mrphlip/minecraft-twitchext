var advancement_data;
function init() {
    var init_state;
    
    // Need to wait for both:
    //  * jQuery is fully inited and fetch our master json
    //  * Twitch is fully inited and passes us the config data
    // which could happen in either order...

    $(function() {
        $.getJSON("advancement_data.json", function(adv_data) {
            Twitch.ext.rig.log('adv_data loaded');
            advancement_data = adv_data;

            if(init_state)
                all_loaded();
        });
    });

    Twitch.ext.configuration.onChanged(function() {
        Twitch.ext.rig.log('init state loaded');
        if (Twitch.ext.configuration.broadcaster) {
            init_state = Twitch.ext.configuration.broadcaster.content;
        } else {
            init_state = 'none';
        }

        if(advancement_data)
            all_loaded();
    });

    function all_loaded() {
        build_page();
        update_page(init_state === 'none' ? undefined : init_state);

        Twitch.ext.listen('broadcast', function (target, contentType, data) {
            Twitch.ext.rig.log('received broadcast data');
            update_page(data);
        });
    }
}
init();

Twitch.ext.onContext(function(context) {
    Twitch.ext.rig.log('context', context);
    document.documentElement.className = 'theme-' + context.theme;
});

function css_class(name) {
    return name.replace(/[:\/]/g, '-');
}

function build_page() {
    $('.content').tabs({
        activate: tile_unclick,
    });
    $('.progress').progressbar({
        max: 1,
        value: 0,
    });

    var detailpane = $('#tab-detail').empty();
    var catpane = {}
    for (var cat of advancement_data.categories) {
        var header = $('<h2>').appendTo(detailpane);
        catpane[cat.id] = $('<div>').appendTo(detailpane);
        header.attr('class', 'catheader labelled');
        $('<span>').attr('class', 'sprite cat-' + css_class(cat.id)).appendTo(header);
        $('<span>').attr('class', 'label').text(cat.name).appendTo(header);
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
    try {
        if (!data)
            throw "Data missing";
        data = RawDeflate.inflate(data);
        data = JSON.parse(data);
    } catch(e) {
        Twitch.ext.rig.log('parse error', e.toString());
        $('.content').hide();
        $('.loadingpane').hide();
        $('.nodata').show();
        return;
    }
    $('.content').show();
    $('.loadingpane').hide();
    $('.nodata').hide();

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
                var lastCrit = undefined;
                for (var i in advdata.criteria)
                    if (!lastCrit || advdata.criteria[i] > lastCrit)
                        lastCrit = advdata.criteria[i];
                advdata.date = lastCrit;
            } else {
                var firstCrit = undefined;
                for (var i in advdata.criteria)
                    if (!firstCrit || advdata.criteria[i] < firstCrit)
                        firstCrit = advdata.criteria[i];
                advdata.date = firstCrit;
            }
            if (!latestadv || advdata.date > latestdata.date) {
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
}

function generate_tooltip() {
    var tile = $(this);
    var panel = $('<div>');
    var adv = tile.data('adv'), advdata = tile.data('advdata');
    panel.attr('class', 'tooltip');
    var header = $('<h3>').appendTo(panel);
    header.attr('class', 'tipheader labelled');
    var icon = $('<span>').attr('class', 'sprite ' + css_class(adv.id)).appendTo(header);
    if (advdata.done)
        icon.addClass('done');
    $('<span>').attr('class', 'label').text(adv.name).appendTo(header);
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
function tile_unclick() {
    if (clicked) {
        $(clicked).tooltip('close');
        clicked = undefined;
    }
}

Twitch.ext.onContext(function(context) {
    Twitch.ext.rig.log('context', context);
    document.documentElement.className = 'theme-' + context.theme;
});

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
            init_state = Twitch.ext.configuration.broadcaster.content || 'none';
        } else {
            init_state = 'none';
        }

        if(advancement_data)
            all_loaded();
    });

    function all_loaded() {
        Twitch.ext.rig.log('all loaded');
        on_loaded();
        on_new_state(parse_data(init_state === 'none' ? undefined : init_state));

        Twitch.ext.listen('broadcast', function (target, contentType, data) {
            Twitch.ext.rig.log('received broadcast data');
            on_new_state(parse_data(data));
        });
    }
}
init();

function parse_data(data) {
    if (!data) {
        Twitch.ext.rig.log("Data missing");
        return undefined;
    }

    try {
        data = atob(data); // un-base64
        data = RawDeflate.inflate(data);
        data = JSON.parse(data);
        return data;
    } catch(e) {
        Twitch.ext.rig.log('parse error', e.toString());
        return undefined;
    }
}

// dummy functions (should be overridden later)
function on_loaded(){}
function on_new_state(data){}

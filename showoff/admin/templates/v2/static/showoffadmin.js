var SHOWOFFADMIN = SHOWOFFADMIN || {};

(function(ns) {
    'use strict';

    var _cfg = {
        'base_url': 'http://showoff_admin',
        'album': 'default'
    };

    var init = function(cfg) {
        $.extend(_cfg, cfg);
    };

    var get = function(key) {
        return _cfg[key];
    };

    var set = function(key, value) {
        _cfg[key] = value;
    };
    
    var glyph = function(icon) {
        return '<span class="glyphicon glyphicon-' + icon + '"></span>';
    };

    var toggle_show = function(element, url, new_url, add) {
        $(element).html('please wait ...');
        var result = $.getJSON(url, false, function() {
            var icon = (add) ? 'ok' : 'remove';
            var new_text = glyph(icon)
            var new_add = (add) ? 'false' : 'true';
            var done_html = '<a href="#" onclick=\'return SHOWOFFADMIN.toggle_show("' + element + '", "' + new_url + '", "' + url + '", ' + new_add + ');\'>' + new_text + '</a>';
            $(element).html(done_html);
        });
        return false;
    };

    var show_toggle_bool = function(element, setting, value) {
        $(element).html('please wait ...');
        var url = ns.get('base_url') + ns.get('album') + '/set/' + setting;
        var result = $.getJSON(url + '/' + value, false, function() {
            var icon = (value == 'yes') ? 'ok' : 'remove';
            var new_text = glyph(icon)
            var new_value = (value == 'yes') ? 'no' : 'yes';
            var done_html = '<a href="#" onclick=\'return SHOWOFFADMIN.toggle_bool("' + element + '", "' + setting + '", "' + new_value + '");\'>' + new_text + '</a>';
            $(element).html(done_html);
        });
        return false;
    };

    // export public functions
    ns.init = init;
    ns.get = get;
    ns.set = set;
    ns.toggle_show = toggle_show;
    ns.toggle_bool = show_toggle_bool;

}(SHOWOFFADMIN));

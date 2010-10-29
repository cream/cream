var applications = {}
var favorites = new Array();

function appToHtml(app, isFavorite){
    var wrapper = new Element('div', {
        'class': 'application',
        events: {
            click: function(){
                if(wrapper.just_dragged)
                    wrapper.just_dragged = false;
                else
                    launch_app(app['cmd'], null);
            },
            drop: function(data){
                launch_app(app['cmd'], data[0]);
            },
            mouseenter: function(){
                wrapper.fade(1);
            },
            mouseleave: function(){
                wrapper.fade(0.7);
            }
        }
    });
    if(isFavorite)
        wrapper.id = 'favorite-' + app['name'];
    else
        wrapper.id = app['name'];

    var icon_wrapper = new Element('div', {'class': 'icon'});
    var icon = new Element('img', {src: 'data:image/png;base64,' + app['icon']});
    var label = new Element('div', {'class': 'label', html: app['label']});
    icon_wrapper.grab(icon);
    wrapper.grab(icon_wrapper);
    wrapper.grab(label);

    //make this element dragable
    wrapper = makeDragable(wrapper);

    //map the id to the app for later use
    applications[wrapper.id] = app;

    wrapper.fade(0.7);
    return wrapper;
}

function fill_dashboard(){
    widget.api.dashboard.get_all_apps(function(apps){
        for(i=0; i < apps.length; i++){
            var category = apps[i];
            var divider = create_divider(category[0]['category'])
            $('dashboard').grab(divider);

            for(j=0; j < category.length; j++){
                var element = appToHtml(category[j], false);
                $('dashboard').grab(element);
            };
        };
        var cleardiv = new Element('div',{styles:'clear:both;'});
        $('dashboard').grab(cleardiv);
    });
}

function load_favorites(){
    widget.api.dashboard.get_favorites(function(favs){
        for(i=0; i < favs.length; i++){
            var element = appToHtml(favs[i], true);
            favorites.push(element);
        };
        update_favorite_bar();
    });
}

function add_favorite(app){
    var element = appToHtml(app, true);
    favorites.push(element);
    update_favorite_bar();
}

function reorder_favorites(element, offset){
    var old_index = favorites.indexOf(element);
    var new_index = old_index + parseInt(offset / 90);
    if (new_index < 0 || new_index > 3 || old_index == new_index)
        return;

    var tmp = new Array(4);
    favorites.each(function(favorite){
        var app = appToHtml(applications[favorite.id], true);
        var index = favorites.indexOf(favorite);
        if(favorite == element)
            tmp[new_index] = app;

        else if(offset > 0){
            if(index < old_index)
                tmp[index] = app;
            else if(index > new_index)
                tmp[index] = app;
            else
                tmp[index - 1] = app;
        } else {
            if(index > old_index)
                tmp[index] = app;
            else if(index < new_index)
                tmp[index] = app;
            else
                tmp[index + 1] = app;
        }
    });

    favorites = tmp;
    update_favorite_bar();
}

function update_favorite_bar(){
    $('favorites').empty();
    var tmp = new Array();
    favorites.each(function(element){
        var app = applications[element.id];
        var element = appToHtml(app, true);
        $('favorites').grab(element);
        tmp.push(element);
    });
    favorites = tmp;
}


function update_dashboard(){
    widget.api.dashboard.update_entries();
    $('dashboard').empty();
    fill_dashboard.delay(500);
}

function create_divider(category){
    var divider = new Element('div', {'class': 'divider', html: category});
    return divider;
}

function launch_app(cmd, arg){
    if(arg)
        widget.api.dashboard.launch_app(cmd, arg);
    else
        widget.api.dashboard.launch_app(cmd, null);
}

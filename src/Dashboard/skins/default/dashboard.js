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
            },
            mousedown: function(e){
                e = new Event(e).stop();

                clone = this.clone()
                    .setStyles(this.getCoordinates())
                    .setStyles({'opacity': 0.7, 'position': 'absolute'})
                    .setStyle('opacity', 0)
                    .setStyle('z-index', 1000)
                    .inject(document.body);

                if(isFavorite)
                    clone.id = 'favorite-' + app['name'];
                else
                    clone.id = app['name'];

                clone.addEvent('mouseup', function() {this.dispose()});

                //make clone draggable
                var drag = makeDragable(clone);

                drag.start(e);
            }
        }
    });

    if(isFavorite)
        wrapper.id = 'favorite-' + app['name'];
    else
        wrapper.id = app['name'];

    var icon_wrapper = new Element('div', {'class': 'icon'});
    if(app['icon'])
        var icon = new Element('img', {src: 'data:image/png;base64,' + app['icon']});
    else
        var icon = new Element('img');

    var label = new Element('div', {'class': 'label', html: app['label']});
    icon_wrapper.grab(icon);
    wrapper.grab(icon_wrapper);
    wrapper.grab(label);

    //map the id to the app for later use
    applications[wrapper.id] = app;

    wrapper.fade(0.7);
    return wrapper;
}

function load_apps(apps){
    var divider = create_divider(apps[0]['category']);
    $('dashboard').grab(divider);
    for(i=0; i < apps.length; i++){
        var app = apps[i];
        var element = appToHtml(app, false);
        $('dashboard').grab(element);

    };
    var cleardiv = new Element('div',{styles:'clear:both;'});
    $('dashboard').grab(cleardiv);
}

function load_favorites(favs){
    /*widget.api.dashboard.get_favorites(function(favs){
        for(i=0; i < favs.length; i++){
            var element = appToHtml(favs[i], true);
            favorites.push(element);
        };
        update_favorite_bar();
    });*/
    for(i=0; i<favs.length; i++){
        var element = appToHtml(favs[i], true);
        favorites.push(element);
    };
    update_favorite_bar();
}

function add_favorite(app){
    var element = appToHtml(app, true);
    if(!contains_favorite(element.id) && favorites.length < 4){
        favorites.push(element);
        widget.api.dashboard.add_favorite(app['name']);
        update_favorite_bar();
    }
}

function contains_favorite(id){
    var contains = false;
    favorites.each(function(el){
        if(el.id == id)
            contains = true;
    });
    return contains;
}

function get_favorite_by_id(id){
    var favorite = null;
    favorites.each(function(el){
        if(el.id == id){
            favorite = el;
        }
    });
    return favorite;
}

function reorder_favorites(element, offset){
    element = get_favorite_by_id(element.id);
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
    $('dashboard').empty();
    $('spinner_overlay').fade('in');
    widget.api.dashboard.update_entries();
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

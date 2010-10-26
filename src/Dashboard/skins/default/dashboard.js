function fill_dashboard(){
    widget.api.dashboard.get_all_apps(function(apps){
        for(i=0; i < apps.length; i++){
            var category = apps[i];
            var divider = create_divider(category[0]['category'])
            $('dashboard').grab(divider);

            for(j=0; j < category.length; j++){
                var app = create_app(category[j]);
                $('dashboard').grab(app);
            };
        };
        cleardiv = new Element('div',{styles:'clear:both;'});
        $('dashboard').grab(cleardiv);
    });
}

function load_favorites(){
    widget.api.dashboard.get_favorites(function(favs){
        for(i=0; i < favs.length; i++){
            add_favorite(create_app(favs[i]));
        };
    });
}

function create_favorite_bar(){
    var favorite_bar = new Element('div',{
        'class': 'favorites',
        id: 'favorites'
    });

    return favorite_bar;
}

function add_favorite(app){
    $('favorites').grab(app);
    favorite_elements.push(app);
}


function update_dashboard(){
    widget.api.dashboard.update_entries();
    $('dashboard').empty();
    fill_dashboard.delay(500);
}

function create_app(app){
    var wrapper = new Element('div', {
        'class': 'app',
        id: app['name'],
        opacity: 0.7,
        events: {
            click: function(){
                if (this.just_dragged)
                    this.just_dragged = false;
                else
                    launch_app(app['cmd'], null);
            },
            drop: function(data){
                launch_app(app['cmd'], data[0]);
            }
        }
    });
    wrapper.just_dragged = false;

    var icon_wrapper = new Element('div', {'class': 'icon'});
    var icon = new Element('img', {src: 'data:image/png;base64,' + app['icon']});
    icon_wrapper.grab(icon);

    var label = new Element('div', {'class': 'label', html: app['name']});

    wrapper.grab(icon_wrapper);
    wrapper.grab(label);

    //make the app draggable
    var drag = new Drag.Move(wrapper, {
        droppables: $$('.favorites', '.scroll'),

        onDrop: function(element, droppable, event){
            wrapper.just_dragged = true;
            wrapper.style.left = 0;
            wrapper.style.top = 0;

            if(droppable && droppable.get('id') == 'favorites'){
                app = create_app(element.app);
                add_favorite(app);
                widget.api.dashboard.add_favorite(app.id);
            }
            if(droppable && droppable.get('class') == 'scroll'){
                if(favorite_elements.contains(element))
                    element.dispose();
            }
        }
    });

    wrapper.app = app;
    return wrapper;
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

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

function create_favorite_bar(){
    var favorite_bar = new Element('div',{
        'class': 'favorites',
        id: 'favorites',
        html: 'hello',
        onDrop: function(){
            alert('dropped');
        },
        onOver: function(){
            alert('over');
        }
    });

    return favorite_bar;
}

function update_dashboard(){
    widget.api.dashboard.update_entries();
    $('dashboard').empty();
    fill_dashboard.delay(500);
}

function create_app(app){
    var wrapper = new Element('div', {
        'class': 'app',
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
    wrapper.makeDraggable({
        onStart:function(){
        },
        onComplete:function(){
            wrapper.just_dragged = true;
            wrapper.style.left = 0;
            wrapper.style.top = 0;
        },
        droppables: $$('.favorites')
    });

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

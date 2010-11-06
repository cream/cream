function makeDragable(application){
    var drag = new Drag.Move(application, {
        droppables: $$('.favorites', '.overlay'),
        container: $('widget'),

        onDrop: function(element, droppable, event){
            if(droppable && droppable.id == 'favorites'){
                if(!favorites.contains(element) && favorites.length < 4){
                    // add this app to favorites
                    var app = applications[element.id];
                    add_favorite(app);
                    widget.api.dashboard.add_favorite(app['name']);
                } else {
                    // reorder favorites
                    var offset = parseFloat(element.style.left.replace('px;'));
                    reorder_favorites(element, offset);
                }
            }
            if(droppable && droppable.id == 'remove'){
                var contains = false;
                var favorite = null;
                favorites.each(function(el){
                    if(el.id == element.id){
                        contains = true;
                        favorite = el;
                    }
                });
                if(contains){
                    favorites.erase(favorite);
                    favorite.dispose();
                    droppable.fade('out');
                    widget.api.dashboard.remove_favorite(element.id.replace('favorite-',''));
                }
            }

            application.just_dragged = true;
            application.style.left = 0;
            application.style.top = 0;
        },
        onStart: function(element){
            favorites.each(function(favorite){
                if(favorite != element)
                    favorite.fade(0.5);
            });
        },
        onComplete: function(element){
            favorites.each(function(element){
                element.fade(0.7);
            });
            cloned_app.dispose();
        },
        onEnter: function(element, droppable){
            if(droppable.id == 'remove' && element.id.test('favorite-'))
                droppable.fade('in');
        },
        onLeave: function(element, droppable){
            if(droppable.id == 'remove' && element.id.test('favorite-'))
                droppable.fade('out');
        }
    });

    return drag;
}

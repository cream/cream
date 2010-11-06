function makeDragable(application){
    var drag = new Drag.Move(application, {
        droppables: $$('.favorites', '.overlay'),
        container: $('widget'),

        onDrop: function(element, droppable, event){
            if(droppable && droppable.id == 'favorites'){
                if(!contains_favorite(element.id) && favorites.length < 4){
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
                var favorite = get_favorite_by_id(element.id);
                if(favorite != null){
                    favorites.erase(favorite);
                    favorite.dispose();
                    widget.api.dashboard.remove_favorite(favorite.id.replace('favorite-',''));
                }
                droppable.fade('out');
            }

            application.just_dragged = true;
            application.style.left = 0;
            application.style.top = 0;
        },
        onStart: function(element){
            element.setStyle('opacity', 1);
            favorites.each(function(favorite){
                if(favorite != element)
                    favorite.fade(0.5);
            });
        },
        onComplete: function(element){
            favorites.each(function(element){
                element.fade(0.7);
            });
            clone.dispose();
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

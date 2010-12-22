var position_start = 0;

function makeDragable(application){
    var drag = new Drag.Move(application, {
        droppables: $$('.favorites', '.overlay'),
        container: $('widget'),

        onDrop: function(element, droppable, event){
            if(droppable && droppable.id == 'favorites'){
                if(!contains_favorite(element.id)){
                    // add this app to favorites
                    var app = applications[element.id];
                    add_favorite(app);
                } else {
                    // reorder favorites
                    position_end = event.page.x;
                    var offset = position_end - position_start;
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
        onStart: function(element, event){
            position_start = event.page.x;
            element.setStyle('opacity', 1);
            favorites.each(function(favorite){
                if(favorite != element)
                    favorite.fade(0.5);
            if(element.id.test('favorite-'))
                $('remove').fade('in');
            });
        },
        onComplete: function(element){
            favorites.each(function(element){
                element.fade(0.7);
            });
            clone.dispose();

            if(element.id.test('favorite-'))
                $('remove').fade('out');
        },
    });

    return drag;
}

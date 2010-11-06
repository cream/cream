var clone = null;
var dummy = null;

function makeDragable(application){
    new Drag.Move(application, {
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
                if(favorites.contains(element)){
                    favorites.erase(element);
                    element.dispose();
                    droppable.fade('out');
                    widget.api.dashboard.remove_favorite(element.id.replace('favorite-',''));
                }
            }

            application.just_dragged = true;
            application.style.left = 0;
            application.style.top = 0;
        },
        onDrag: function(element, event){
            if(clone != null)
                element.setPosition({'x': event.page.x - 50, 'y': event.page.y - 50});

        },
        onStart: function(element){
            if(!favorites.contains(element)){
                dummy = {'name':'','label':'','icon':false,'cmd':''};
                dummy = appToHtml(dummy);

                dummy.replaces(element);
                $('widget').grab(element, 'top');

                element.setStyle('position', 'absolute');

                clone = element;
            }

            favorites.each(function(favorite){
                if(favorite != element)
                    favorite.fade(0.5);
            });
        },
        onComplete: function(element){
            if(clone != null){
                clone.replaces(dummy);
                clone.setStyle('position', 'relative');
                clone = null;
                dummy = null;
            }
            favorites.each(function(element){
                element.fade(0.7);
            });
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

    return application;
}

var ProgressBar = new Class({
    initialize: function(elm, update_interval) {
        this.interval_id = null;
        this.position = 0;
        this.update_interval = update_interval
        var canvas = $(elm);
        this.width = parseInt(canvas.get('width'));
        this.height = parseInt(canvas.get('height'));
        this.ctx = canvas.getContext('2d');
        this.ctx.fillStyle = "rgba(120,120,120,0.3)";
        this.ctx.strokeStyle = "rgba(40,40,40,0.8)";
        this.ctx.lineWidth = 2;
    },
    start: function(duration, current_position) {
        this.reset();
        this.duration = duration;
        this.px_per_iteration = this.update_interval * (this.width / duration);
        this.position = (this.width / duration) * current_position;
        this.interval_id = this.draw.periodical(this.update_interval * 1000, this);
    },
    pause: function(){
        this.interval_id = $clear(this.interval_id);
    },
    stop: function() {
        this.pause();
        this.reset();
    },
    resume: function(){
        this.interval_id = this.draw.periodical(this.update_interval * 1000, this);
    },
    reset: function(){
        this.position = 0;
        this.interval_id = $clear(this.interval_id);
        this.draw();
    },
    draw: function() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.draw_background();
        this.ctx.beginPath();

        var position = parseInt(this.position);
        this.ctx.moveTo(0,3);
        this.ctx.lineTo(position, 3);
        this.ctx.lineTo(position, this.height - 3);
        this.ctx.lineTo(0, this.height - 3);
        this.ctx.fill();
        this.position = this.position + this.px_per_iteration;
    },
    draw_background: function(){
        this.ctx.moveTo(0,0);
        this.ctx.lineTo(this.width, 0);
        this.ctx.lineTo(this.width, this.height);
        this.ctx.lineTo(0, this.height);
        this.ctx.lineTo(0,0);
        this.ctx.stroke();
    }
});

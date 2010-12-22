var ms = 0;
var state = 0;
var interval;

function two(x) {return ((x>9)?"":"0")+x}
function three(x) {return ((x>99)?"":"0")+((x>9)?"":"0")+x}

function split_time(ms) {
    var sec = Math.floor(ms/1000)
    ms = ms % 1000
    t = three(ms)

    var min = Math.floor(sec/60)
    sec = sec % 60
    t = two(sec) + ":" + t

    var hr = Math.floor(min/60)
    min = min % 60
    t = two(min) + ":" + t

    hr = hr % 60
    t = two(hr) + ":" + t
    
    return [hr, min, sec, ms]
}

function startstop() {
    if (state == 0) {
        state = 1;
        btn = document.getElementById("startstop_button")
        btn.setAttribute("class", "button red");
        btn.innerHTML = "Stop"
        then = new Date();
        then.setTime(then.getTime() - ms);
        interval = setInterval("update();", 50);
    } else {
        state = 0;
        btn = document.getElementById("startstop_button")
        btn.setAttribute("class", "button green");
        btn.innerHTML = "Start"
        now = new Date();
        ms = now.getTime() - then.getTime();
        if (typeof(interval) != 'undefined') {
            clearInterval(interval);
        }
    }
}

function reset() {
    ms = 0;
    then = new Date();
    update()
}

function update() {
        now = new Date();
        ms = now.getTime() - then.getTime();
    
        t = split_time(ms);
    
        h = t[0] + ""
        if (h.length < 2) {
            h = "0" + h
            }
    
        m = t[1] + ""
        if (m.length < 2) {
            m = "0" + m
            }
    
        s = t[2] + ""
        if (s.length < 2) {
            s = "0" + s
            }

        ms = Math.round(t[3]/10) + ""
        if (ms.length < 2) {
            ms = "0" + ms
            }
        if (ms.length > 2) {
            ms = ms.slice(0, 2)
            }
    
        document.getElementById('main').innerHTML = h + ":" + m + ":" + s;
        document.getElementById('ms').innerHTML = "." + ms;
}

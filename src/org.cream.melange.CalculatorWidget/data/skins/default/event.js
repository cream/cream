function check_key_events(e) {

    var key_id = (window.event) ? event.keyCode : e.keyCode;

    switch(key_id) {
        case 48: add_number(0); break;
        case 49: add_number(1); break;
        case 50: add_number(2); break;
        case 51: add_number(3); break;
        case 52: add_number(4); break;
        case 53: add_number(5); break;
        case 54: add_number(6); break;
        case 55: add_number(7); break;
        case 56: add_number(8); break;
        case 57: add_number(9); break;
        case 188: add_number('.'); break;
        case 190: add_number('.'); break;

        case 107: set_command('+'); break;
        case 109: set_command('-'); break;
        case 189: set_command('-'); break;
        case 106: set_command('*'); break;
        case 111: set_command('/'); break;
        case 191: set_command('/'); break;

        case 187: calc(true); break;
        case 13: calc(true); break;

        case 46: reset_display(); break;
        case 67: reset_display(); break;
    }

}

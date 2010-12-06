var BEFORE = 'before';
var AFTER = 'after';
var TYPE_DEFAULT = 'default-operator';
var TYPE_SPECIAL = 'special-operator';

var last_command = '';
var last_command_type = TYPE_DEFAULT;
var last_number = '';
var act_number = '';

var special_commands = new Array();
special_commands['SQRT'] = Array('√', 'Math.sqrt(%i)', BEFORE);
special_commands['EXP'] = Array('^', 'Math.pow(%i, %ii)', AFTER);

var commands = new Array();
commands['+'] = '+';
commands['-'] = '−';
commands['*'] = '×';
commands['/'] = '÷';

function round_float(num, n) {
	num = (Math.round(num * n) / n);
   	return num;
}

function add_number(num) {
	act_number = act_number + num;

	if (document.getElementById('lcd').innerHTML == '0') {
		document.getElementById('lcd').innerHTML = act_number;
	}
	else {
		document.getElementById('lcd').innerHTML += num;
	}
}

function reset_display() {
	last_command = '';
    last_command_type = TYPE_DEFAULT;
	last_number = '';
	act_number = '';
	document.getElementById('lcd').innerHTML = '0';
}

function set_command(command, special) {
	last_number = calc(false);
	last_command = command;
	act_number = '';
    if (special == true) {
        last_command_type = TYPE_SPECIAL;
        if (special_commands[command][2] == BEFORE) {
        	document.getElementById('lcd').innerHTML = special_commands[command][0] + document.getElementById('lcd').innerHTML;
        }
        else if (special_commands[command][2] == AFTER) {
        	document.getElementById('lcd').innerHTML += special_commands[command][0];
        }
    }
    else {
        last_command_type = TYPE_DEFAULT;
    	document.getElementById('lcd').innerHTML += commands[command];
    }
}

function calc(display) {
    if (last_command_type == TYPE_DEFAULT) {
    	sum = round_float(eval(last_number + last_command + act_number), 1000000);
    }
    else if (last_command_type == TYPE_SPECIAL) {
        com = special_commands[last_command][1].replace('%i', last_number);
        com = com.replace('%ii', act_number);
        sum = round_float(eval(com), 1000000);
    }

    if (display == true) {
    	document.getElementById('lcd').innerHTML = sum;
    }
    
    act_number = '';
	last_number = sum;
    last_command = '';
    last_command_type = TYPE_DEFAULT;

	return sum;
}

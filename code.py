import time
import board
import adafruit_fancyled.adafruit_fancyled as fancy
import adafruit_trellism4
import usb_midi
import adafruit_midi

from color_names import * # pylint: disable=wildcard-import,unused-wildcard-import

trellis = adafruit_trellism4.TrellisM4Express()
pages = []

def hex_to_color(int_color):
    red = int_color >> 16
    green = (int_color >> 8) & 254
    blue = (int_color & 254)
    return red,green,blue

def map_key_number(input):
    return input[0] + (8 * input[1])

def key_to_number(input):
    if input > 23:
        return input - 24, 3
    elif input > 15:
        return input - 16, 2
    elif input > 7:
        return input - 8, 1
    else:
        return input, 0

def map(value, in_min, in_max, out_min, out_max):
   return(value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def fade_color(color,fade):
    if (fade == 0):
        return 0,0,0
    elif (fade == 255):
        return color
    else:
        r_in,g_in,b_in = color
        r = int(map(fade,0,255,0,r_in))
        g = int(map(fade,0,255,0,g_in))
        b = int(map(fade,0,255,0,b_in))
        return r,g,b

def render_page(page,fade):
    if(len(pages) > page):
        for x in range(0,32):
            if(x >= len(pages[page])):
                trellis.pixels[key_to_number(x)] = 0,0,0
            else:
                render_page_key(page,x,fade)
    else:
        print("Don't have page to render")

def render_page_key(page,key,fade):
    color = 0,0,0
    if key != 31:
        if pages[page][key]["color"].startswith("0x"):
            color = hex_to_color((int)(pages[page][key]["color"]))
        else:
            color = hex_to_color(palette[pages[page][key]["color"]])
    else:
        color = hex_to_color(palette[color_set[page]])
    trellis.pixels[key_to_number(key)] = fade_color(color,fade)

def generate_page(pg_num):
    pages.insert(pg_num, [])
    for x in range(0,32):
        (pages[pg_num]).insert(x,{})
        if(pg_num != 31):
            pages[pg_num][x]["color"] = "0x0"
        else:
            pages[pg_num][x]["color"] = color_set[x]
        pages[pg_num][x]["text"] = ""

for i in range(0,32):
    generate_page(i)

#Load Table
lines = [line.rstrip('\n') for line in open('data.csv')]

for line in lines[1:]:
    row = line.split(',')
    #Page exists?
    pg_num = int(row[0])
    assert pg_num < 31
    btn_num = int(row[1])
    assert btn_num < 31, "BTN_Number over 30"
    pages[pg_num][btn_num]["color"] = row[2]
    pages[pg_num][btn_num]["text"] = row[3]

#Boot on Page 0
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
print("Setting default output MIDI channel:", midi.out_channel + 1)
page = 0
render_page(page,255)
page_no = 0
mode = "page"
last_state = []
lit_led = []
key_pressed_xy = 0
key_pressed = -1
key_offset = 0
timeout = 0
timeout_set = 10000
fade_level = 0

while True:
    pressed = trellis.pressed_keys
    if pressed != last_state:
        last_state = pressed
        if len(pressed) == 0:
            if lit_led != -1:
                render_page_key(page_no,key_pressed,255)
            if key_pressed != -1:
                midi.note_off(key_pressed + key_offset, 127)
                key_pressed = -1;
        elif len(pressed) == 1:
            key_pressed_xy = pressed[0]
            key_pressed = map_key_number(pressed[0])
            lit_led = pressed[0]
            if(mode == "timeout"):
                print ("Out of timeout")
                mode = "page"
                render_page(page_no,255)
                timeout = 0
            else:
                trellis.pixels[lit_led] = 255,255,255
                if mode == "page":
                    if key_pressed == 31:
                        print("Switch to select mode")
                        mode = "select"
                        render_page(31,255)
                    else:
                        midi.note_on(key_pressed + key_offset, 127)
                elif mode == "select":
                    if key_pressed == 31:
                        print("Double-tap page key")
                    else:
                        page_no = map_key_number(pressed[0])
                        if(key_pressed > 15):
                            chan_no = page_no - 15
                            key_offset = 32
                        else:
                            chan_no = page_no
                            key_offset = 0
                        print("Changing Page to ",page_no)
                        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=chan_no)
                        render_page(page_no,255)
                        mode = "page"
        else:
            print("Too Many buttons pressed")
    elif(pressed == []):
        timeout += 1
        if(mode == "timeout" and timeout % 10 == 0 and fade_level > 0):
            fade_level -= 5
            render_page(page_no,fade_level)
        elif(timeout == timeout_set):
            print("Timeout")
            mode = "timeout"
            fade_level = 255
    #else: print("key_held")
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import necessary libraries for communication and display use
import drivers
import subprocess
from time import sleep

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = drivers.Lcd()

# Function to get the output of the specified screen session
def get_screen_session_output(session_name):
    capture_command = f'screen -S {session_name} -X hardcopy /tmp/screen_output.txt'
    subprocess.run(capture_command, shell=True)
    with open('/tmp/screen_output.txt', 'r') as file:
        output = file.read().strip()
    return output

# Function to display scrolling text on the LCD
def display_scrolling_text(display, text='', num_line=1, num_cols=16):
    """
    Parameters: (driver, string to print, number of line to print, number of columns of your display)
    This function sends text to display as scrolling text.
    """
    if len(text) > num_cols:
        display.lcd_display_string(text[:num_cols], num_line)
        sleep(1)
        for i in range(len(text) - num_cols + 1):
            text_to_print = text[i:i+num_cols]
            display.lcd_display_string(text_to_print, num_line)
            sleep(0.2)
        sleep(1)
    else:
        display.lcd_display_string(text, num_line)

# Main body of code
try:
    print("Press CTRL + C to stop this script!")

    while True:
        # Get the output of the specified screen session
        session_output = get_screen_session_output("goesrecv")

        # Display the output as scrolling text on the LCD
        display_scrolling_text(display, session_output, 1)  # Assuming single line display

except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()

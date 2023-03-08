from pyvirtualdisplay import Display
with Display() as disp:
    # display is active
    print(disp.is_alive()) # True
# display is stopped
print(disp.is_alive()) # False
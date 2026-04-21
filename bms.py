import os
import time
from wave_lib import LCD_2inch
from PIL import Image, ImageDraw, ImageFont
from ina226 import INA226

# FONT SETUP
font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28
)

print("starting display")

# LCD SETUP
disp = LCD_2inch.LCD_2inch()
disp.Init()
disp.bl_DutyCycle(50)

# INA226 SETUP
SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.5

ina = INA226(
    shunt_ohms=SHUNT_OHMS,
    max_expected_amps=MAX_EXPECTED_AMPS,
    address=0x40
)

ina.configure()
ina.wake()

# BATTERY CONFIG
voltage = ina.voltage() 
BATTERY_CAPACITY_AH = 2.2
SOC = (voltage - 10.5) / (12.6 - 10.5) * 100
SOC = max(0, min(100,SOC))
last_time = time.time()

#self shutdown 
count = 0


print("starting loop")

while True:
    now = time.time()
    dt = now - last_time
    last_time = now

    # SENSOR READINGS
    current_A = ina.current() / 1000  #  Amps
    voltage = ina.voltage()     # Volts

    # COULOMB COUNTING
    SOC = 0.97 * (SOC - (current_A*dt)/( 3600 * BATTERY_CAPACITY_AH) *100) + 0.03 * ((voltage - 10.5)/(12.6 -10.5) *100)
    # Clamp
    SOC = max(0, min(100, SOC))

    print(f"I: {current_A:.2f}A | V: {voltage:.2f}V | SOC: {SOC:.1f}%")

  
    # DRAW SCREEN
    if SOC >= 25:
        
        image = Image.new("RGB", (disp.height, disp.width), "WHITE")
        draw = ImageDraw.Draw(image)
    
    # Text
        draw.text((30, 20), f"Voltage: {voltage:.2f}V", fill="black", font=font)
        draw.text((30, 60), f"Current: {current_A:.2f}A", fill="black", font=font)
        draw.text((60, 100), f"SOC: {SOC:.1f}%", fill="black", font=font)

    # Battery bar
        bar_width = int((SOC / 100) * 200)
        draw.rectangle((70, 150, 270, 180), outline="black", width=2)
        draw.rectangle((70, 150, 70 + bar_width, 180), fill="black")
    
    else:
        image = Image.new("RGB", (disp.height, disp.width), "RED")
        draw = ImageDraw.Draw(image)
        draw.text((30, 20), f"Voltage: {voltage:.2f}V", fill="black", font=font)
        draw.text((5, 70), f"Charge The Battery", fill="black", font=font)
        draw.text((60, 100), f"SOC: {SOC:.1f}%", fill="black", font=font)
        #draw.text((5, 200), f" {count*5:.1f}", fill="black", font=font)
        bar_width = int((SOC / 100) * 200)
        draw.rectangle((70, 150, 270, 180), outline="black", width=2)
        draw.rectangle((70, 150, 70 + bar_width, 180), fill="black")
        '''
        #shut off (entirely optional)
        count+=1
        
        if count>=12:
            running=False
            os.system("sudo shutdown now")
        '''
    disp.ShowImage(image)
    

    time.sleep(5)

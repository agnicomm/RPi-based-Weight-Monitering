import RPi.GPIO as GPIO
import time
import smtplib
from datetime import datetime
from urllib.request import urlopen
 
# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

DT = 5
SCK = 6

# Define GPIO to LED mapping
LED_G = 17
LED_R  = 4
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME  = 'softchipacc@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD  = 'pwd'  #change this to match your gmail password

class Emailer:
       def sendmail(self, recipient, subject, content):
          
        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
  
        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
  
        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit
  
def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(SCK, GPIO.OUT) # DB7
  GPIO.setup(LED_G, GPIO.OUT) # LED GREEN
  GPIO.setup(LED_R, GPIO.OUT) # LED RED

  now = datetime.now() # current date and time
	# Enter Your API key here  

  myAPI = 'YYJN3A8SQKWZJII6'
	# URL where we will send the data, Don't change it
  baseURL = 'https://api.thingspeak.com/update?api_key=%s'%myAPI

  # Initialise display
  lcd_init()
  lcd_string("Rasbperry Pi IoT",LCD_LINE_1)
  lcd_string("Fire Extinguisher",LCD_LINE_2)
  time.sleep(1) # 2 second delay
  # Send some text
  lcd_string("Rajesh Sharma  ",LCD_LINE_1)
  lcd_string("6 Week Project  ",LCD_LINE_2)
  time.sleep(1) # 2 second delay
  lcd_string("Clean Agent Wt. ",LCD_LINE_1)
  # frequency = 1
  isEmailSent = False
  threshold = 70.000
  sender = Emailer()
  while True:
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    lcd_string(date_time,LCD_LINE_1)
    time.sleep(1)	 
    count= readCount()
    w=0
    w=((count/106) / 1000)
    w=round(w,3)
    if w>threshold:
      lcd_string("Clean Agent OK. ",LCD_LINE_1)
      GPIO.output(LED_G,1)
      GPIO.output(LED_R,0)
      
    elif w<threshold:
      lcd_string("Clean Agent LOW ",LCD_LINE_1)
      GPIO.output(LED_R,1)
      GPIO.output(LED_G,0)
      if isEmailSent == False:
        sendTo  =  'agnicomm@gmail.com'
        emailSubject  =  "Fire Clean Agent LOW"
        emailContent  =  "Clean Agent LOW "  +  time.ctime()
        sender.sendmail(sendTo, emailSubject, emailContent)
        lcd_string("Email:-Sent  Low  ",LCD_LINE_1)
        isEmailSent = True
      
	#if(w > threshold):
	#if true:
     # lcd_string("Clean Agent OK. ",LCD_LINE_1)
    #lcd_string(str(frequency)+". Weight",LCD_LINE_1)
    strVal = str(w) + ' kg' 
    lcd_string(strVal,LCD_LINE_2)
    time.sleep(1)
    # Sending the data to thingspeak
    conn = urlopen(baseURL + '&field1=%s' % (str(w)))
    print (conn.read())    
    #frequency=frequency + 1
    #conn.close()

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
lcd_byte(ord(message[i]),LCD_CHR)

def readCount():
  i=0
  Count=0
  print (Count)
  time.sleep(0.001)
  GPIO.setup(DT, GPIO.OUT)
  GPIO.output(DT,1)
  GPIO.output(SCK,0)
  GPIO.setup(DT, GPIO.IN)

  while GPIO.input(DT) == 1:
      i=0
  for i in range(24):
        GPIO.output(SCK,1)
        Count=Count<<1

        GPIO.output(SCK,0)
        time.sleep(0.001)
        if GPIO.input(DT) == 0: 
            Count=Count+1
            print (Count)
        
  GPIO.output(SCK,1)
  Count=Count^0x800000
  time.sleep(0.001)
  GPIO.output(SCK,0)
  return Count  
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("bye!",LCD_LINE_1)
    GPIO.cleanup()

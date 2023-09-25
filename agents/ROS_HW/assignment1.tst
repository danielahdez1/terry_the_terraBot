BASELINE = assignment1.bsl

# Wait a minute before starting, to give agent a chance to initialize
DELAY FOR 60

# Turn pump on when dry
WHENEVER smoist[0] < 500 or smoist[1] < 500
  # Wait a long time b/c watering behavior is not scheduled very often
  WAIT wpump FOR 14400
  WAIT not wpump FOR 360 # Turn pump off before 6 minutes have elapsed
  # Wait an hour for both moisture sensors to be above threshold
  WAIT smoist[0] > 500 and smoist[1] > 500 FOR 3600

# Don't let the pump overwater things
WHENEVER wpump
  ENSURE smoist[0] < 600 and smoist[1] < 600 FOR 3600

WHENEVER 1-22:00:00
  # Wait for 6 minutes for lights to go off after 10pm each day
  WAIT not led FOR 360

WHENEVER 1-22:10:00
  # Ensure lights stay off until just before 6am the next day
  ENSURE not led UNTIL 2-05:55:55

# When temperature is high, make sure the fan turns on for at least a minute
WHENEVER temperature[0] > 29 or temperature[1] > 29
  WAIT fan FOR 1800
  ENSURE fan FOR 60

# When temperature is low between 6am and 10pm, and lights not already on
#  make sure the lights turn on for at least two minutes
WHENEVER temperature[0] < 22 and temperature[1] < 22 and not led and (mtime//3600) >= 6 and (mtime//3600) < 22
  WAIT led FOR 14400
  ENSURE led FOR 120

# When the humidity is high, make sure the fan turns on for at least a minute
WHENEVER humidity[0] > 90 or humidity[1] > 90
  WAIT fan FOR 1800
  PRINT "FAN ON at %s (humidity %d)" %(clock_time(time), humidity[0])
  ENSURE fan FOR 60

QUIT AT 3-23:59:59 # Run the test and simulator for 3 days

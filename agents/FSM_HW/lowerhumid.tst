# Wait a minute before starting, to give agent a chance to initialize
DELAY FOR 60

# When the LowerHumid behavior is enabled and the temperature is high,
#  the fan should turn on within a minute
WHENEVER enabled('LowerHumidBehavior') and (humidity[0]+humidity[0])/2 > limits['humidity'][1]
  WAIT fan FOR 60

# When the LowerHumid behavior is enabled, the fan should be off after it 
#  is disabled
WHENEVER enabled('LowerHumidBehavior')
  WAIT not enabled('LowerHumidBehavior') FOR 1800 # 30 minutes
  ENSURE not fan

QUIT AT 2-23:59:59

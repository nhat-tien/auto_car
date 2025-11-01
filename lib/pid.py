import time
from parameter import FILTER_NOISE
from calculate_control_signal import calculate_angle

class PID:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        self.time_extract = time.monotonic
        self.last_time = self.time_extract()
        self.last_state = None
        self.integral = 0
        self.close_integral = False

    def __call__(self, state):
        state = self.noise_filter(state)
        error = self.setpoint - state
        # kd = 0 if abs(error) < 5 else self.kd
        d_state = state - (self.last_state if (self.last_state is not None) else state)
        d_error = -d_state

        now = self.time_extract()
        d_time = now - self.last_time
        d_time = d_time if (d_time) else 1e-12

        # P
        proportional = self.kp*error
        # I
        # if not self.close_integral:
        self.integral += self.ki*error*d_time
        # D
        derivative = self.kd*d_error/d_time
       

        control_signal = proportional + derivative
        if not self.close_integral:
            control_signal += self.integral
        # print(proportional,self.integral,derivative)

        self.close_integral = self.anti_windup(error, control_signal)

        self.last_time = now
        self.last_state = state

        return control_signal

    def noise_filter(self, state):
        d_state = state - (self.last_state if (self.last_state is not None) else state)
        if abs(d_state) > FILTER_NOISE:
            return self.last_state
        else:
            return state
    
    def anti_windup(self, error, control_signal_before):
        control_signal_after = calculate_angle(control_signal_before, True, 60)
        return control_signal_before != control_signal_after and (error * control_signal_before > 0)



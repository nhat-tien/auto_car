import time

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

    def __call__(self, state):
        error = self.setpoint - state
        kd = 0 if abs(error) < 5 else self.kd
        d_state = state - (self.last_state if (self.last_state is not None) else state)
        d_error = -d_state

        now = self.time_extract()
        d_time = now - self.last_time
        d_time = d_time if (d_time) else 1e-12

        # P
        proportional = self.kp*error
        # I
        self.integral += self.ki*error*d_time
        # D
        derivative = self.kd*d_error/d_time

        control_signal = proportional + self.integral + derivative

        self.last_time = now
        self.last_state = state

        return control_signal

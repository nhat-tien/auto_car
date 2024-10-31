def calculate_angle(num, angle_control_enable, max_error_to_full_angle):
    if not angle_control_enable:
        return num
    max = max_error_to_full_angle
    if num < -max or num > max:
        return 1 if num > 0 else -1
    else:
        return (1/max)*(num)

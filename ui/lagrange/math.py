import math

def find_collision_point(ellipse_points, inside_point, outside_point):
    x1, y1 = inside_point
    x2, y2 = outside_point

    closest_point = None
    min_distance = float('inf')

    # Direction vector from inside point to outside point
    dx, dy = x2 - x1, y2 - y1
    line_length = math.sqrt(dx**2 + dy**2)

    for ex, ey in ellipse_points:
        # Vector from inside point to ellipse point
        fx, fy = ex - x1, ey - y1
        
        # Project the ellipse point onto the line
        t = (fx * dx + fy * dy) / (line_length ** 2)

        if 0 <= t <= 1:
            # Calculate the closest point on the line segment
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

            # Distance from ellipse point to the closest point on the line
            distance = math.sqrt((ex - closest_x) ** 2 + (ey - closest_y) ** 2)

            if distance < min_distance:
                min_distance = distance
                closest_point = (ex, ey)

    return closest_point

def rotate_vector(dx, dy, angle_degrees):
    # Convert the angle to radians
    angle_radians = math.radians(angle_degrees)
    
    # Calculate the new vector components after rotation
    new_dx = dx * math.cos(angle_radians) - dy * math.sin(angle_radians)
    new_dy = dx * math.sin(angle_radians) + dy * math.cos(angle_radians)
    
    return new_dx, new_dy

def find_point_on_line(point1, point2, distance):
    x1, y1 = point1
    x2, y2 = point2
    
    d_AB = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    unit_vector_x = (x2 - x1) / d_AB
    unit_vector_y = (y2 - y1) / d_AB
    
    x = x1 + distance * unit_vector_x
    y = y1 + distance * unit_vector_y
    
    return (x, y)
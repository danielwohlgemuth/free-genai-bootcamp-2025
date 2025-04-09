def str_to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    
    truthy_values = ('true', '1', 't', 'yes', 'on')
    falsy_values = ('false', '0', 'f', 'no', 'off')
    
    if value is None:
        return default
        
    value = str(value).lower()
    if value in truthy_values:
        return True
    if value in falsy_values:
        return False
    
    return default
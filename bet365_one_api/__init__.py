t = 1
if t:
    try:
        from .all_modules import *
    except Exception as er:
        from all_modules import *
else:
    pass

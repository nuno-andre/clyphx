
def get_python_info(serialize=True):
    import sys
    import json

    version_info = {k: getattr(sys.version_info, k) for k in
                    ('major', 'minor', 'micro', 'releaselevel', 'serial')}

    modules = {k: {'module': getattr(v, '__name__', None),
                   'file': getattr(v, '__file__', None)}
               for k, v in sys.modules.items()}

    info = {
        'version':         sys.version,
        'version_info':    version_info,
        'path':            sys.path,
        'modules':         modules,
        'builtin_modules': sys.builtin_module_names,
        'executable':      sys.executable,
        # 'dllhandle':       sys.dllhandle,
        'exec_prefix':     sys.exec_prefix,
    }

    return json.dumps(info, indent=4) if serialize else info

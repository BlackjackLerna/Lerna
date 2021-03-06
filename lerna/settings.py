import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_logging(cnf):
    import logging.config

    if 'handlers' in cnf:
        for handler in cnf['handlers'].values():
            if 'filename' in handler:
                os.makedirs(os.path.dirname(handler['filename']), exist_ok=True)

    logging.logThreads = logging.logProcesses = False
    return logging.config.dictConfig(cnf)


def _init_settings():
    import yaml

    def adjust_path(loader, node): return os.path.join(BASE_DIR, loader.construct_scalar(node))
    yaml.add_constructor('!path', adjust_path)

    configuration_files = ('settings.yml', 'static/settings.yml', 'local_settings.yml')
    for filename in configuration_files:
        with open(os.path.join(BASE_DIR, 'lerna', filename), encoding='utf-8-sig') as f:
            for yml_key, yml_data in yaml.load(f).items():
                if yml_key == 'PREPEND':
                    for key, value in yml_data.items():
                        globals()[key] = value + globals()[key]
                elif yml_key == 'APPEND':
                    for key, value in yml_data.items():
                        globals()[key] += value
                elif yml_key == 'OVERRIDE':
                    for cnf_name, sub_data in yml_data.items():
                        cnf = globals()[cnf_name]
                        for key, value in sub_data.items():
                            cnf[key] = value
                else:
                    globals()[yml_key] = yml_data

    # TODO: Log every failure.
    try:
        import pypandoc as pd
    except ImportError:
        pass
    else:
        try:
            pd.get_pandoc_version()
        except OSError:
            pass
        else:
            output = pd.convert_text('', 'html', format='latex')
            if output not in ('', '\n'):
                raise Exception('pandoc is found, but has not passed a sample test (%r)' % output)

            def check_filter(f):
                try:
                    pd.convert_text('', 'html', format='latex', filters=[f])
                    return True
                except RuntimeError:
                    return False

            PANDOC['REQUIRED'] = True
            PANDOC['FILTERS'] = list(filter(check_filter, PANDOC['FILTERS']))


_init_settings()

import os
import sys
import pkg_resources

def locate():
    path = pkg_resources.resource_filename(__name__, 'pymacaron_deploy_configs/Dockerfile.template')
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__))
    return path

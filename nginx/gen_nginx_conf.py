import os
import sys
from tornado import template

with open(sys.argv[1], encoding="utf8") as f:
    nginx_template = f.read()

substs = dict()

substs["dev_mode"] = os.environ.get("dev_mode", "false") == "true"
substs["dns_server"] = os.environ["dns_server"]

t = template.Template(nginx_template)
print(t.generate(**substs).decode(encoding='utf-8', errors='strict'))


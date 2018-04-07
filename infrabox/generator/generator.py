import shutil
import json
import os
import copy
import re

def push_latest(tag):
    r = r'^[0-9]\.[0-9]\.[0-9]$'
    match = re.match(r, tag)

    if match:
        return True

    return False

def main():
    shutil.copyfile('/generator/infrabox.json', '/infrabox/output/infrabox.json')
    shutil.copyfile('/generator/e2e.json', '/infrabox/output/e2e.json')
    shutil.copyfile('/generator/tests.json', '/infrabox/output/tests.json')

    deployments = None
    with open('/generator/deployments.json') as dep:
        deployments = json.load(dep)

    tag = os.environ.get('INFRABOX_GIT_TAG', None)

    # modify tags
    for j in deployments['jobs']:
        deps = j.get('deployments', [])
        if not deps:
            continue

        new_deps = []

        for d in deps:
            new_dep_tag = copy.deepcopy(d)
            new_dep_dev = copy.deepcopy(d)
            new_dep_latest = copy.deepcopy(d)

            new_dep_tag['tag'] = tag
            new_dep_dev['tag'] = 'dev'
            new_dep_latest['tag'] = 'latest'

            new_deps.append(d)

            if tag:
                new_deps.append(new_dep_tag)

                if push_latest(tag):
                    new_deps.append(new_dep_latest)
            else:
                new_deps.append(new_dep_dev)

        j['deployments'] = new_deps

    # Disable caches for tag builds
    for j in deployments['jobs']:
        j['cache'] = {
            'image': False,
            'data': False
        }

    branch = os.environ.get('INFRABOX_GIT_BRANCH', None)
    if not branch:
        for j in deployments['jobs']:
            if 'deployments' in j:
                del j['deployments']


    with open('/infrabox/output/deployments.json', 'w') as out:
        json.dump(deployments, out)

if __name__ == "__main__":
    main()

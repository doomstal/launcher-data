import os
from os import path
import platform
import sys
import json
import urllib
import shutil
import zipfile

dataRoot = "data"

defaultLibraryUrl = "https://libraries.minecraft.net/"
assetsDownloadUrl = "http://resources.download.minecraft.net/";

if len(sys.argv) < 2:
    print("list profiles:  setup.py -l")
    print("use profile:    setup.py profile_name")
    exit(1)

if platform.system() == 'Windows':
    minecraftRoot = os.getenv('APPDATA')
else:
    minecraftRoot = os.path.expanduser('~')
minecraftRoot += os.sep + ".minecraft"

print("minecraftRoot="+minecraftRoot)

print("dataRoot="+dataRoot)

if sys.argv[1] == '-l':
    for f in os.listdir(minecraftRoot+os.sep+"versions"):
        p = path.join(minecraftRoot, "versions", f)
        if path.isdir(p) and path.isfile(p+os.sep+f+".json"):
            print(f)
    exit(0)

conf = {'libraries': []}

def lib2name(lib, nat = None):
    lib = lib.split(':')
    if nat:
        return lib[1]+'-'+lib[2]+'-'+nat+'.jar'
    else:
        return lib[1]+'-'+lib[2]+'.jar'

def lib2path(lib):
    parts = lib.split(':')
    return path.join(parts[0].replace('.', path.sep), parts[1], parts[2])

def copy_or_download(url, src, dst):
    if path.isfile(dst):
        return
    dstdir = path.dirname(dst)
    if not path.exists(dstdir):
        os.makedirs(dstdir)
    if path.isfile(src):
        print("copying "+dst)
        shutil.copyfile(src, dst)
        return
    print("downloading "+dst)
    urllib.urlretrieve(url, dst)

def extract(file):
    print("extracting "+file)
    dst = path.dirname(file)
    z = zipfile.ZipFile(open(file, 'rb'))
    for name in z.namelist():
        if 'META-INF' in name:
            continue
        z.extract(name, dst)
    z.close()
    if path.exists(file):
        os.remove(file)

def read_version(v):
    data = json.load(open(path.join(minecraftRoot, "versions", v, v+".json")))
    if 'inheritsFrom' in data:
        read_version(data['inheritsFrom'])

    global conf
    if 'id' in data: conf['version'] = data['id']
    if 'assets' in data: conf['assets'] = data['assets']
    if 'mainClass' in data: conf['mainClass'] = data['mainClass']
    if 'minecraftArguments' in data: conf['minecraftArguments'] = data['minecraftArguments']
    if 'jar' in data: conf['jar'] = data['jar']
    if 'downloads' in data: conf['jarUrl'] = data['downloads']['client']['url']
    if 'assetIndex' in data: conf['assetIndex'] = data['assetIndex']
    if 'libraries' in data: conf['libraries'].extend(data['libraries'])

read_version(sys.argv[1])
if 'jar' not in conf: conf['jar'] = conf['version']

copy_or_download(
    conf['jarUrl'],
    path.join(minecraftRoot, "versions", conf['jar'], conf['jar']+'.jar'),
    path.join(dataRoot, "versions", conf['jar']+'.jar')
)

for lib in conf['libraries']:
    oses = {
        'windows': True,
        'linux': True,
        'osx': True
    }
    if 'rules' in lib:
        for n in oses: oses[n] = False
        for r in lib['rules']:
            if 'os' in r:
                oses[r['os']['name']] = (r['action'] == 'allow')
            else:
                for n in oses: oses[n] = (r['action'] == 'allow')
    if 'downloads' in lib:
        if 'artifact' in lib['downloads']:
            dst = []
            if all(v for v in oses.values()):
                dst.append("libraries")
            else:
                for n in oses:
                    if oses[n]: dst.append("libraries"+path.sep+n)
            for f in dst:
                copy_or_download(
                    lib['downloads']['artifact']['url'],
                    path.join(minecraftRoot, "libraries", lib2path(lib['name']), lib2name(lib['name'])),
                    path.join(dataRoot, f, lib2name(lib['name']))
                )
    elif 'url' in lib or 'serverreq' in lib or 'clientreq' in lib: # forge
        if 'url' not in lib: lib['url'] = defaultLibraryUrl
        copy_or_download(
            lib['url']+path.join(lib2path(lib['name']), lib2name(lib['name'])).replace('\\', '/'),
            path.join(minecraftRoot, "libraries", lib2path(lib['name']), lib2name(lib['name'])),
            path.join(dataRoot, "libraries", "forge", lib2name(lib['name']))
        )
    else:
        print(lib)
    if 'natives' in lib:
        for nat in lib['natives']:
            if not oses[nat]: continue
            if '${arch}' in lib['natives'][nat]: continue
            url = lib['downloads']['classifiers'][ lib['natives'][nat] ]['url']
            src = path.join(minecraftRoot, "libraries", lib2path(lib['name']), lib2name(lib['name'], lib['natives'][nat]))
            dst = path.join(dataRoot, "natives", nat, lib2name(lib['name'], lib['natives'][nat]))
            copy_or_download(url, src, dst)
            extract(dst)

asset_file = path.join(dataRoot, "assets", "indexes", conf['assetIndex']['id']+'.json')
copy_or_download(
    conf['assetIndex']['url'],
    path.join(minecraftRoot, "assets", "indexes", conf['assetIndex']['id']+'.json'),
    asset_file
)
data = json.load(open(asset_file))
for obj in data['objects']:
    hash = data['objects'][obj]['hash']
    copy_or_download(
        assetsDownloadUrl+hash[0:2]+'/'+hash,
        path.join(minecraftRoot, "assets", "objects", hash[0:2], hash),
        path.join(dataRoot, "assets", "objects", hash[0:2], hash)
    )

jarArgsIgnore = {
    '--username',
    '--uuid',
    '--accessToken',
    '--userProperties',
    '--userType',
    '--gameDir',
    '--assetsDir'
}
jarArgsValues = {
    '${version_name}': conf['version'],
    '${assets_index_name}' : conf['assets'],
}
jarArgs = []

args = conf['minecraftArguments'].split()
for i in range(0, len(args), 2):
    if args[i] in jarArgsIgnore:
        continue
    jarArgs.append(args[i])
    if args[i+1] in jarArgsValues:
        args[i+1] = jarArgsValues[args[i+1]]
    jarArgs.append(args[i+1])

print("writing manifest.sh")
manifest_config = "mainClass;" + conf['mainClass'] + "\njar;" + "\njar;".join(jarArgs)

open(path.join(dataRoot, 'manifest.sh'), 'w').write(
    open('manifest.sh.tpl', 'r').read().replace('MANIFEST_CONFIG', manifest_config)
)
open(path.join(dataRoot, 'manifest.txt'), 'w').write(manifest_config)

print("done")
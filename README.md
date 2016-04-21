### launcher manual:

in short, launcher expects following directory structure:

```assets
libraries
libraries/linux
libraries/macosx
libraries/windows
minecraft
natives
natives/linux
natives/macosx
natives/windows
versions
```

1. create empty directory and all subdirectories. (`data` in this manual)
2. move your `.minecraft` somewhere and run vanilla launcher to download a clean copy of desired minecraft version.
3. open `.minecraft/versions/1.x/1.x.json`. find `"libraries"` section. it contains a list of all needed libraries.
look for apropriate jars in `.minecraft/libraries/...` and copy them to `data/libraries`.
**note** that some libraries have `"rules"` section which usually describes if they are OS-specific.
put such libraries in apropriate OS-specific subfolder.
also vanilla launcher will download libraries for your OS only, use links in json to download them manually.
4. same with natives. look for `"natives"`, find jars and extract libraries to OS-specific subfolders in `data/natives`.
they should contain `.dll`, `.so` and `.dynlib` for windows, linux and macosx respectively. don't extract `META-INF`.
5. copy `.minecraft/versions/1.x/1.x.jar` to `data/versions`
6. copy `.minecraft/assets` to `data/assets`. it should contain assets for your minecraft version only, because you have clean installation. usually it contains assets for all installed minecraft versions.
7. mods, resource packs, etc goes in `data/minecraft`.

### testing

create `data/manifest.txt` with following contents: (substitute your minecraft version)
```
jar;--version
jar;1.x
jar;--assetIndex
jar;1.x
mainClass;net.minecraft.client.main.Main
```

put `launcher.jar` in your `data` library and run it with `local` command line argument.

### deployment

put `manifest.sh` in your `data` folder, open it and substitute your minecraft version.
it generates `manifest.txt`, containing list of files, their sizes and sha1 sums.
you may either run it on your server or locally and manually upload `manifest.txt`.

if you want to have default files, which are downloaded only once and not being overwriten during update (e.g. minecraft's options.txt or servers.dat),
create `data/_userfile/minecraft` and put them there. launcher will download them if only they are missing.
the `_userfile` affix only used to indicate that file can be modified by user, and stripped when downloading.

make `assets.zip` for `assets` folder to speed up installation a little. launcher will try to download and extract assets from it, and fallback to downloading asset files one-by-one on failure.

### forge

install forge as usual and copy libraries listed in it's profile's `json` file like described above.
I find it convinient to put them in `data/libraries/forge`, but it's not necessary.

forge adds extra jar arguments and uses custom main class, so you'll need to update `manifest.sh` as well.

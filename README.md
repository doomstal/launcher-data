### installation

`setup.py -l` to get list of available profiles

`setup.py profile_name` to select profile. it will copy/download all necessary files into `data` directory

after installation you will get following directory structure inside `data`:
```
assets -- minecraft asset files
libraries -- common libraries
libraries/forge -- forge specific libraries (if you installed forge profile)
libraries/linux -- linux specific libraries
libraries/osx -- macosx specific libraries
libraries/windows -- windows specific libraries
minecraft -- game directory. mods, resourcepacks, etc goes here
natives
natives/linux -- linux .so libraries
natives/osx -- macosx .dylib .jnilib libraries
natives/windows -- windows .dll libraries
versions -- game jar
```

### testing

put `launcher.jar` in `data` library and run it with `local` command line argument.

### deployment

upload `data` directory somewhere and point launcher's `baseUrl` to it.
run `manifest.sh` either on your server or locally and upload `manifest.txt` manually

make `assets.zip` from `assets` folder and put it in your `data` directory. this will speed up launcher's first run.

you'll want to have default config files for minecraft. put them in `data/_userfile/minecraft`. launcher will download them if only they are missing. the `_userfile` affix only used to indicate that file can be modified by user and stripped when downloading.

### forge

install forge as usual, and select forge profile when installing.

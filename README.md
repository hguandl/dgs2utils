# dgs2utils
Pack utilities for The Great Ace Attorney 2 on 3DS

## Usage

### Text files - GMD

```
$ python3 -m dgs2utils.gmd
usage: python3 -m gmd [-h] {unpack,repack} ...

Pack and unpack GMD files.

optional arguments:
  -h, --help       show this help message and exit

commands:
  {unpack,repack}  GMD process
    unpack         Unpack GMD files
    repack         Repack to GMD
```

### Font files - GFD

```
$ python3 -m dgs2utils.gfd
usage: python3 -m gfd [-h] {dump,generate,export} ...

Processing GFD files.

optional arguments:
  -h, --help            show this help message and exit

commands:
  {dump,generate,export}
                        GFD process
    dump                Unpack GMD files
    generate            Repack to GMD
    export              Export GMD
```

### Font bitmap picture - TEX
Note: Only implemented for font textures with only alpha channel.

```python
from dgs2utils import tex
from PIL import Image

# TEX to PNG
with open('sample.tex', 'rb') as f:
  mt_tex = tex.MTTex.load(f)
  mt_tex.export_png('sample.png')

# PNG to TEX
with open('sample.png', 'rb') as f:
  img = Image.open(f)
  mt_tex = tex.MTTex.new(img.size, img.getdata())
  mt_tex.export_tex('sample.tex')
```

### Collect characters for font generation
```
$ python3 -m dgs2utils.font_db
usage: font_db.py [-h] {count,from_csv,merge} ...

Process list of font characters.

optional arguments:
  -h, --help            show this help message and exit

commands:
  {count,from_csv,merge}
                        Font list process
    count               Count characters from text files
    from_csv            Generate font list from CSV
    merge               Merge lists
```

## Credit
The specs of files are learned from [Kurrimu](https://github.com/IcySon55/Kuriimu).

## LICENSE

Apache-2.0 License

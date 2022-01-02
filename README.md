# NFT Art Generator

Plugin for Maya that generates unique render from a collection of component trait based on weight.

![](pic/4x4.jpg)

![](pic/ui.jpg)
### Dependencies

- Maya2018 and up
- Python 2.7




## Usage
Component asset structure.

layers/
├─ trait_type1
│  ├─ trait1
│  ├─ trait2
│  ├─ trait3
│  ├─ ...
├─ trait_type2
│  ├─ trait1
│  ├─ trait2
│  ├─ ...
├─ trait_type3
│  ├─ trait1
│  ├─ ...
├─ ...

![](pic/outliner.jpg)

## Install
copy everything to C:\Users\user\Documents\maya\2018\scripts

```python
import gen_main
import ui
import farm_ui
import farm_submission
ui.runMayaTemplateUi()
```
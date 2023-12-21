# 多python包管理项目

多python包管理项目

## 目录结构
```
src
├── ca-lark-sdk
│   ├── connectai
│   │   └── lark
│   │       └── sdk
│   │           └── __init__.py
│   ├── LICENSE
│   ├── README.md
│   └── setup.py
└── connectai
    ├── connectai
    │   └── __init__.py
    ├── LICENSE
    ├── README.md
    └── setup.py

7 directories, 8 files
```

# build

```
python setup.py egg_info --egg-base /tmp sdist --dist-dir=`pwd`/dist

dist
├── ca-lark-sdk-0.0.1.tar.gz
└── connectai-0.0.10.tar.gz
```

# 本地安装

```
pip install dist/*


site-packages/connectai
├── __init__.py
├── lark
│   └── sdk
│       ├── __init__.py
│       └── __pycache__
│           └── __init__.cpython-310.pyc
└── __pycache__
    └── __init__.cpython-310.pyc

5 directories, 4 files

>>> import connectai
>>> import connectai.lark.sdk
>>> connectai.__version__
'0.0.10'
>>> connectai.lark.sdk.__version__
'0.0.1'
```
